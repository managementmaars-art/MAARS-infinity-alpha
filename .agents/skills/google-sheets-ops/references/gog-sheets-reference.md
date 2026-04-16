# gog sheets コマンドリファレンス

## コマンド一覧

| コマンド | 用途 |
|---|---|
| `gog sheets create` | スプレッドシート新規作成 |
| `gog sheets get` | セル値の読み取り |
| `gog sheets update` | セル値の書き込み（上書き） |
| `gog sheets append` | 行の追加 |
| `gog sheets clear` | セル値のクリア |
| `gog sheets format` | 書式設定 |
| `gog sheets metadata` | スプレッドシート情報取得 |
| `gog sheets copy` | スプレッドシートのコピー |
| `gog sheets export` | PDF/XLSX/CSV出力 |

---

## ⚠️ 最重要: 値の区切りルール

**セル区切り: パイプ `|`**
**行区切り: カンマ `,`**

```bash
# ✅ 正しい: パイプでセル区切り + 範囲を明示
gog sheets update "$ID" "Sheet!A1:C1" "値1|値2|値3"

# ❌ 間違い: スペース区切り → 全部1セルに結合される
gog sheets update "$ID" "Sheet!A1:C1" "値1" "値2" "値3"

# ❌ 間違い: 範囲がA1だけ → パイプがあっても1セルに入る可能性
gog sheets update "$ID" "Sheet!A1" "値1|値2|値3"
```

### 複数行を一度に書く
```bash
# カンマで行区切り、パイプでセル区切り
gog sheets update "$ID" "Sheet!A1:C2" "ヘッダ1|ヘッダ2|ヘッダ3,値1|値2|値3"
```

### JSON形式での値指定（推奨: 複雑なデータ向け）
```bash
# カンマやパイプを含むデータも安全に書ける
gog sheets update "$ID" "Sheet!A1:C2" --values-json '[["名前","金額","備考"],["田中","500,000","初回|特別"]]'
```

### appendも同様
```bash
# ✅ 正しい
gog sheets append "$ID" "Sheet!A:C" "値1|値2|値3"

# ✅ JSON形式
gog sheets append "$ID" "Sheet" --values-json '[["値1","値2","値3"]]'
```

---

## create - スプレッドシート作成

```bash
# 基本（タブ1つ: デフォルト名「シート1」）
gog sheets create "タイトル"

# 複数タブ付きで作成（⚠️ 後からタブ追加はgogでは不可能）
gog sheets create "タイトル" --sheets "クライアント,プロジェクト,タスク,設定"
```

**重要: `--sheets`を使わないとタブは1つだけ。gogにはタブの後追加・削除・リネーム機能がない。必ずcreate時に全タブを指定する。**

---

## get - 値の読み取り

```bash
gog sheets get "$ID" "シート名!A1:D10"        # テーブル表示
gog sheets get "$ID" "シート名!A1:D10" --json  # JSON出力（プログラム処理向け）
gog sheets get "$ID" "シート名!A1:D10" --plain # TSV出力
```

**--json出力で確認すべきこと:** 値が正しくセル分離されているか（配列の要素数=列数）

---

## update - 値の書き込み

```bash
# 基本: パイプ区切り + 範囲明示
gog sheets update "$ID" "シート!A1:D1" "A|B|C|D"

# 複数行
gog sheets update "$ID" "シート!A1:C3" "名前|年齢|部署,田中|30|営業,佐藤|25|開発"

# JSON形式（カンマ・パイプを含むデータに安全）
gog sheets update "$ID" "シート!A1:C2" --values-json '[["項目","金額"],["サービスA","1,500,000"]]'

# 数式を書く
gog sheets update "$ID" "シート!D2:D2" "=SUM(B2:C2)"

# 数式を文字列として書く（計算させない）
gog sheets update "$ID" "シート!A1:A1" "=SUM(B1:B10)" --input RAW

# 入力規則をコピー
gog sheets update "$ID" "シート!A2:A100" "値" --copy-validation-from "シート!A2:A2"
```

**--input オプション:**
- `USER_ENTERED`（デフォルト）: 数式は計算、日付は日付として解釈
- `RAW`: すべて文字列として保存

---

## append - 行追加

```bash
# シート名 or 列範囲で指定
gog sheets append "$ID" "シート!A:D" "値1|値2|値3|値4"

# JSON形式
gog sheets append "$ID" "シート" --values-json '[["値1","値2","値3"]]'

# 既存行を下にずらして挿入
gog sheets append "$ID" "シート" "値" --insert INSERT_ROWS
```

---

## clear - クリア

```bash
gog sheets clear "$ID" "シート!A1:Z1000"   # 全クリア
gog sheets clear "$ID" "シート!A2:A100"     # 特定範囲
```

---

## format - 書式設定

`--format-json` に Google Sheets API の CellFormat JSON を渡す。
`--format-fields` でどのフィールドを適用するか指定。

### CellFormat の主要フィールド

| フィールド | 型 | 説明 |
|---|---|---|
| `backgroundColor` | `{red,green,blue,alpha}` | 背景色（0.0〜1.0） |
| `textFormat` | object | フォント設定 |
| `textFormat.bold` | bool | 太字 |
| `textFormat.italic` | bool | 斜体 |
| `textFormat.strikethrough` | bool | 取り消し線 |
| `textFormat.underline` | bool | 下線 |
| `textFormat.fontSize` | int | フォントサイズ |
| `textFormat.foregroundColor` | `{red,green,blue}` | 文字色 |
| `textFormat.fontFamily` | string | フォント名 |
| `horizontalAlignment` | string | `LEFT`/`CENTER`/`RIGHT` |
| `verticalAlignment` | string | `TOP`/`MIDDLE`/`BOTTOM` |
| `wrapStrategy` | string | `OVERFLOW_CELL`/`WRAP`/`CLIP` |
| `numberFormat` | `{type,pattern}` | 数値フォーマット |
| `borders` | object | 罫線 |

### よく使う書式パターン

**ヘッダー（青背景・白太字）:**
```bash
gog sheets format "$ID" "シート!A1:H1" \
  --format-json '{"backgroundColor":{"red":0.2,"green":0.4,"blue":0.7},"textFormat":{"bold":true,"foregroundColor":{"red":1,"green":1,"blue":1}}}' \
  --format-fields "userEnteredFormat(backgroundColor,textFormat)"
```

**太字のみ:**
```bash
gog sheets format "$ID" "シート!A1:A10" \
  --format-json '{"textFormat":{"bold":true}}' \
  --format-fields "userEnteredFormat.textFormat.bold"
```

**背景色（黄色ハイライト）:**
```bash
gog sheets format "$ID" "シート!A1:H1" \
  --format-json '{"backgroundColor":{"red":1,"green":0.95,"blue":0.8}}' \
  --format-fields "userEnteredFormat.backgroundColor"
```

**中央揃え:**
```bash
gog sheets format "$ID" "シート!A1:H1" \
  --format-json '{"horizontalAlignment":"CENTER"}' \
  --format-fields "userEnteredFormat.horizontalAlignment"
```

**テキスト折り返し:**
```bash
gog sheets format "$ID" "シート!A1:H100" \
  --format-json '{"wrapStrategy":"WRAP"}' \
  --format-fields "userEnteredFormat.wrapStrategy"
```

**数値フォーマット（カンマ区切り）:**
```bash
gog sheets format "$ID" "シート!G2:G100" \
  --format-json '{"numberFormat":{"type":"NUMBER","pattern":"#,##0"}}' \
  --format-fields "userEnteredFormat.numberFormat"
```

**日付フォーマット:**
```bash
gog sheets format "$ID" "シート!F2:F100" \
  --format-json '{"numberFormat":{"type":"DATE","pattern":"yyyy/mm/dd"}}' \
  --format-fields "userEnteredFormat.numberFormat"
```

**罫線（下線のみ）:**
```bash
gog sheets format "$ID" "シート!A1:H1" \
  --format-json '{"borders":{"bottom":{"style":"SOLID","color":{"red":0,"green":0,"blue":0}}}}' \
  --format-fields "userEnteredFormat.borders"
```

**複合書式（複数フィールドを一度に）:**
```bash
gog sheets format "$ID" "シート!A1:H1" \
  --format-json '{"backgroundColor":{"red":0.2,"green":0.4,"blue":0.7},"textFormat":{"bold":true,"foregroundColor":{"red":1,"green":1,"blue":1},"fontSize":11},"horizontalAlignment":"CENTER","borders":{"bottom":{"style":"SOLID","color":{"red":0,"green":0,"blue":0}}}}' \
  --format-fields "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,borders)"
```

---

## metadata - スプレッドシート情報

```bash
gog sheets metadata "$ID"          # タブ一覧・行列数
gog sheets metadata "$ID" --json   # JSON出力
```

**用途:** タブ名の確認（日本語ロケールだと「シート1」）、シートID取得

---

## copy - コピー

```bash
gog sheets copy "$ID" "コピー先タイトル"
gog sheets copy "$ID" "コピー先タイトル" --parent "フォルダID"
```

---

## export - エクスポート

```bash
gog sheets export "$ID" --format csv
gog sheets export "$ID" --format xlsx
gog sheets export "$ID" --format pdf
```

---

## Drive連携（ファイル操作）

```bash
gog drive mkdir "フォルダ名"                              # フォルダ作成
gog drive move "$ID" --parent "フォルダID"                # ファイル移動
gog drive rename "$ID" "新しい名前"                       # リネーム
gog drive share "$ID" --email "user@example.com" --role writer  # 共有
```

---

## gogで**できない**こと（Google Sheets API直接 or GAS が必要）

| 機能 | 代替手段 |
|---|---|
| タブの後追加・削除・リネーム | Sheets API `batchUpdate` の `addSheet`/`deleteSheet`/`updateSheetProperties` |
| 入力規則（ドロップダウン等）の設定 | Sheets API `batchUpdate` の `setDataValidation` |
| 条件付き書式 | Sheets API `batchUpdate` の `addConditionalFormatRule` |
| セル結合 | Sheets API `batchUpdate` の `mergeCells` |
| 列幅・行高の調整 | Sheets API `batchUpdate` の `updateDimensionProperties` |
| 行/列の固定（フリーズ） | Sheets API `batchUpdate` の `updateSheetProperties` (frozenRowCount) |
| 列/行の自動リサイズ | Sheets API `batchUpdate` の `autoResizeDimensions` |
| フィルター設定 | Sheets API `batchUpdate` の `setBasicFilter` |
| チャート作成 | Sheets API `batchUpdate` の `addChart` |
| シートの保護 | Sheets API `batchUpdate` の `addProtectedRange` |

### Sheets API batchUpdate を使うには

gogからは直接叩けない。以下の方法が必要:
1. **Node.js googleapis** パッケージ（`npm install googleapis`）
2. **clasp + GAS** でApps Script経由
3. **curl** + OAuthトークン（gogのkeychain経由は難しい場合あり）

トークンの取得が課題。gogはmacOS Keychainにトークンを保存しており、`security find-generic-password -s "gogcli" -w` で取得可能だが、Touch ID/パスワードプロンプトが出る場合がある。

### keyring backend を file に変更する方法（headless対応）

```bash
# fileバックエンドに切り替え
gog auth keyring file

# 環境変数でパスワード設定
export GOG_KEYRING_PASSWORD='your-password'

# これでsecurity コマンド不要になる
```

---

## SpreadsheetID の取得

URLから: `https://docs.google.com/spreadsheets/d/<ここがID>/edit`

---

## 日本語環境の注意

- デフォルトシート名: `シート1`（Sheet1ではない）
- `gog sheets metadata` で正確なシート名を必ず確認
- シート名にスペースや特殊文字がある場合はシングルクォートで囲む: `'シート 1'!A1:B2`

---

## よくあるミスと対策

| ミス | 症状 | 対策 |
|---|---|---|
| スペース区切りで値を渡す | 全部1セルに結合 | パイプ `\|` 区切りにする |
| 範囲を`A1`だけにする | 1セルにしか書けない | `A1:C1`のように終点も指定 |
| create後にタブ追加しようとする | コマンドがない | `--sheets`で最初に全部作る |
| カンマ含む値をパイプ区切りで書く | 意図しない行分割 | `--values-json`を使う |
| metadataを確認せずシート名を推測 | range parse error | 必ず`metadata`で確認 |
