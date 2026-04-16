# Z-Image 圖片生成工具 (Antigravity Skill)

這是一個基於 ModelScope **Z-Image** 模型的圖片生成工具。它可以讓你在終端機 (Terminal) 輸入簡單的指令，即刻生成高品質的 AI 圖片。

## 🌟 功能特點
- **高品質生成**：使用阿里雲開發的 Z-Image 模型，支持中英文提示詞。
- **異步處理**：完美解決大模型生成時間較長的問題，自動排隊並獲取結果。
- **多種配置方式**：支持直接修改代碼、命令列參數或 `.env` 配置文件，靈活且安全。

## 🛠️ 安裝與準備

### 1. 安裝環境
確保你的電腦已安裝 Python 3，然後安裝必要的套件：
```bash
pip install requests python-dotenv
```

### 2. 獲取 API Key
1. 註冊並登入 [ModelScope 魔搭社區](https://modelscope.cn/)。
2. 在「個人中心」獲取你的 API Key。
3. **重要**：請確保你的 ModelScope 帳號已綁定「阿里雲帳號」，否則 API 會返回認證錯誤。

### 3. 設定 API Key (三選一)
- **方法 A (最直觀)**：打開 `scripts/generate_zimage.py`，在大約第 18 行的 `DEFAULT_API_KEY` 處填入你的 Key。
- **方法 B (推薦)**：在 `scripts/` 資料夾下建立一個 `.env` 檔案，內容如下：
  ```text
  MODELSCOPE_API_TOKEN="你的Key"
  ```
- **方法 C (臨時用)**：執行指令時加上 `--api-key "你的Key"`。

## 🚀 使用方法

在終端機輸入以下指令：

```bash
python3 scripts/generate_zimage.py "一隻正在宇宙中漫步的可愛金色貓咪，4k畫質，精緻細節"
```

### 常用參數：
- `--output` 或 `-o`: 指定輸出的路徑與檔名（預設為自動生成）。
- `--size` 或 `-s`: 指定圖片尺寸（預設 1024x1024）。
- `--api-key` 或 `-k`: 臨時指定 API Key。

## 📁 檔案結構
- `SKILL.md`: 供 Antigravity AI Agent 讀取的技能說明文檔。
- `scripts/generate_zimage.py`: 核心 Python 腳本。
- `scripts/.env.example`: 環境變數配置文件範例。

## 📝 授權說明
本項目僅供學習與交流使用。模型版權歸 ModelScope/Alibaba 所有。
