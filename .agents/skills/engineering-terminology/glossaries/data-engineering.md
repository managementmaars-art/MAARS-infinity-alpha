# Data Engineering Terminology

## Overview

This glossary covers data engineering concepts including databases, data pipelines, ETL/ELT processes, data warehousing, analytics, and big data technologies. Use this for data architecture documentation, pipeline specifications, and database content.

## Database Fundamentals

| English             | Japanese                   | Chinese (Traditional) | Notes                                         |
| ------------------- | -------------------------- | --------------------- | --------------------------------------------- |
| Database            | データベース               | 資料庫                | Often abbreviated DB                          |
| DBMS                | DBMS                       | DBMS                  | Database Management System                    |
| SQL                 | SQL                        | SQL                   | Structured Query Language                     |
| NoSQL               | NoSQL                      | NoSQL                 | Not Only SQL                                  |
| Relational Database | リレーショナルデータベース | 關聯式資料庫          | RDBMS                                         |
| Table               | テーブル                   | 表                    | Database table                                |
| Row                 | 行                         | 列                    | Table row/record                              |
| Column              | 列                         | 欄                    | Table column                                  |
| Record              | レコード                   | 記錄                  | Database record                               |
| Field               | フィールド                 | 欄位                  | Database field                                |
| Primary Key         | 主キー                     | 主鍵                  | -                                             |
| Foreign Key         | 外部キー                   | 外鍵                  | -                                             |
| Index               | インデックス               | 索引                  | -                                             |
| Schema              | スキーマ                   | 綱要                  | Database schema                               |
| View                | ビュー                     | 檢視                  | Database view                                 |
| Stored Procedure    | ストアドプロシージャ       | 預存程序              | -                                             |
| Trigger             | トリガー                   | 觸發程序              | -                                             |
| Transaction         | トランザクション           | 交易                  | -                                             |
| ACID                | ACID                       | ACID                  | Atomicity, Consistency, Isolation, Durability |
| Commit              | コミット                   | 提交                  | -                                             |
| Rollback            | ロールバック               | 回滾                  | -                                             |
| Constraint          | 制約                       | 約束                  | -                                             |
| Normalization       | 正規化                     | 正規化                | Data normalization                            |
| Denormalization     | 非正規化                   | 反正規化              | -                                             |

## Query & Operations

| English            | Japanese         | Chinese (Traditional) | Notes             |
| ------------------ | ---------------- | --------------------- | ----------------- |
| Query              | クエリ           | 查詢                  | -                 |
| SELECT             | SELECT           | SELECT                | SQL SELECT        |
| INSERT             | INSERT           | INSERT                | SQL INSERT        |
| UPDATE             | UPDATE           | UPDATE                | SQL UPDATE        |
| DELETE             | DELETE           | DELETE                | SQL DELETE        |
| JOIN               | 結合             | 聯結                  | SQL JOIN          |
| INNER JOIN         | 内部結合         | 內部聯結              | -                 |
| LEFT JOIN          | 左外部結合       | 左聯結                | -                 |
| RIGHT JOIN         | 右外部結合       | 右聯結                | -                 |
| FULL JOIN          | 完全外部結合     | 完全聯結              | -                 |
| WHERE              | WHERE            | WHERE                 | SQL WHERE clause  |
| GROUP BY           | GROUP BY         | GROUP BY              | SQL GROUP BY      |
| ORDER BY           | ORDER BY         | ORDER BY              | SQL ORDER BY      |
| HAVING             | HAVING           | HAVING                | SQL HAVING        |
| Subquery           | サブクエリ       | 子查詢                | -                 |
| Aggregate Function | 集約関数         | 彙總函數              | -                 |
| COUNT              | COUNT            | COUNT                 | SQL COUNT         |
| SUM                | SUM              | SUM                   | SQL SUM           |
| AVG                | AVG              | AVG                   | SQL AVG (average) |
| MAX                | MAX              | MAX                   | SQL MAX           |
| MIN                | MIN              | MIN                   | SQL MIN           |
| Filter             | フィルタ         | 篩選                  | -                 |
| Sort               | ソート           | 排序                  | -                 |
| Pagination         | ページネーション | 分頁                  | -                 |

## NoSQL Databases

| English             | Japanese                 | Chinese (Traditional) | Notes                                          |
| ------------------- | ------------------------ | --------------------- | ---------------------------------------------- |
| Document Database   | ドキュメントデータベース | 文件資料庫            | -                                              |
| Key-Value Store     | キーバリューストア       | 鍵值儲存              | -                                              |
| Column-Family Store | カラムファミリーストア   | 列族儲存              | -                                              |
| Graph Database      | グラフデータベース       | 圖資料庫              | -                                              |
| MongoDB             | MongoDB                  | MongoDB               | Keep as-is                                     |
| Redis               | Redis                    | Redis                 | Keep as-is                                     |
| Cassandra           | Cassandra                | Cassandra             | Keep as-is                                     |
| DynamoDB            | DynamoDB                 | DynamoDB              | Keep as-is                                     |
| Neo4j               | Neo4j                    | Neo4j                 | Keep as-is                                     |
| Collection          | コレクション             | 集合                  | NoSQL collection                               |
| Document            | ドキュメント             | 文件                  | NoSQL document                                 |
| Key                 | キー                     | 鍵                    | -                                              |
| Value               | 値                       | 值                    | -                                              |
| Node                | ノード                   | 節點                  | Graph node                                     |
| Edge                | エッジ                   | 邊                    | Graph edge                                     |
| Relationship        | リレーションシップ       | 關係                  | Graph relationship                             |
| Sharding            | シャーディング           | 分片                  | -                                              |
| Replication         | レプリケーション         | 複製                  | -                                              |
| CAP Theorem         | CAP定理                  | CAP定理               | Consistency, Availability, Partition tolerance |

## Data Warehousing

| English                   | Japanese                       | Chinese (Traditional) | Notes                         |
| ------------------------- | ------------------------------ | --------------------- | ----------------------------- |
| Data Warehouse            | データウェアハウス             | 資料倉儲              | DWH                           |
| Data Mart                 | データマート                   | 資料超市              | -                             |
| Data Lake                 | データレイク                   | 資料湖                | -                             |
| Data Lakehouse            | データレイクハウス             | 資料湖倉              | -                             |
| OLAP                      | OLAP                           | OLAP                  | Online Analytical Processing  |
| OLTP                      | OLTP                           | OLTP                  | Online Transaction Processing |
| Star Schema               | スタースキーマ                 | 星型綱要              | -                             |
| Snowflake Schema          | スノーフレークスキーマ         | 雪花綱要              | -                             |
| Fact Table                | ファクトテーブル               | 事實表                | -                             |
| Dimension Table           | ディメンションテーブル         | 維度表                | -                             |
| Measure                   | メジャー                       | 量值                  | -                             |
| Dimension                 | ディメンション                 | 維度                  | -                             |
| Grain                     | 粒度                           | 粒度                  | Data granularity              |
| Slowly Changing Dimension | 緩やかに変化するディメンション | 緩慢變化維度          | SCD                           |
| Aggregate                 | 集約                           | 彙總                  | -                             |
| Cube                      | キューブ                       | 立方體                | OLAP cube                     |
| Drill Down                | ドリルダウン                   | 向下鑽取              | -                             |
| Drill Up                  | ドリルアップ                   | 向上鑽取              | -                             |
| Slice and Dice            | スライスアンドダイス           | 切片                  | -                             |
| Roll Up                   | ロールアップ                   | 上卷                  | -                             |

## ETL/ELT Processes

| English              | Japanese             | Chinese (Traditional) | Notes                    |
| -------------------- | -------------------- | --------------------- | ------------------------ |
| ETL                  | ETL                  | ETL                   | Extract, Transform, Load |
| ELT                  | ELT                  | ELT                   | Extract, Load, Transform |
| Extract              | 抽出                 | 擷取                  | -                        |
| Transform            | 変換                 | 轉換                  | -                        |
| Load                 | ロード               | 載入                  | -                        |
| Data Pipeline        | データパイプライン   | 資料流水線            | -                        |
| Data Flow            | データフロー         | 資料流                | -                        |
| Data Integration     | データ統合           | 資料整合              | -                        |
| Data Migration       | データ移行           | 資料遷移              | -                        |
| Batch Processing     | バッチ処理           | 批次處理              | -                        |
| Stream Processing    | ストリーム処理       | 串流處理              | -                        |
| Real-Time Processing | リアルタイム処理     | 即時處理              | -                        |
| Incremental Load     | 増分ロード           | 增量載入              | -                        |
| Full Load            | 全量ロード           | 全量載入              | -                        |
| Delta Load           | デルタロード         | 差異載入              | -                        |
| Change Data Capture  | 変更データキャプチャ | 異動資料擷取          | CDC                      |
| Data Validation      | データ検証           | 資料驗證              | -                        |
| Data Cleansing       | データクレンジング   | 資料清洗              | -                        |
| Data Quality         | データ品質           | 資料品質              | -                        |
| Data Deduplication   | 重複排除             | 資料去重              | -                        |

## Big Data Technologies

| English             | Japanese           | Chinese (Traditional) | Notes                          |
| ------------------- | ------------------ | --------------------- | ------------------------------ |
| Big Data            | ビッグデータ       | 大數據                | -                              |
| Hadoop              | Hadoop             | Hadoop                | Keep as-is                     |
| HDFS                | HDFS               | HDFS                  | Hadoop Distributed File System |
| MapReduce           | MapReduce          | MapReduce             | Keep as-is                     |
| Spark               | Spark              | Spark                 | Apache Spark                   |
| Kafka               | Kafka              | Kafka                 | Apache Kafka                   |
| Flink               | Flink              | Flink                 | Apache Flink                   |
| Hive                | Hive               | Hive                  | Apache Hive                    |
| Presto              | Presto             | Presto                | Keep as-is                     |
| Airflow             | Airflow            | Airflow               | Apache Airflow                 |
| Distributed System  | 分散システム       | 分散式系統            | -                              |
| Cluster             | クラスタ           | 叢集                  | -                              |
| Node                | ノード             | 節點                  | Cluster node                   |
| Master Node         | マスターノード     | 主節點                | -                              |
| Worker Node         | ワーカーノード     | 工作節點              | -                              |
| Partition           | パーティション     | 分割區                | Data partition                 |
| Data Locality       | データローカリティ | 資料局部性            | -                              |
| Parallel Processing | 並列処理           | 平行處理              | -                              |
| DAG                 | DAG                | DAG                   | Directed Acyclic Graph         |
| Job                 | ジョブ             | 作業                  | -                              |
| Task                | タスク             | 任務                  | -                              |

## Data Storage Formats

| English         | Japanese               | Chinese (Traditional) | Notes                      |
| --------------- | ---------------------- | --------------------- | -------------------------- |
| CSV             | CSV                    | CSV                   | Comma-Separated Values     |
| JSON            | JSON                   | JSON                  | JavaScript Object Notation |
| XML             | XML                    | XML                   | eXtensible Markup Language |
| Parquet         | Parquet                | Parquet               | Keep as-is                 |
| Avro            | Avro                   | Avro                  | Keep as-is                 |
| ORC             | ORC                    | ORC                   | Optimized Row Columnar     |
| Columnar Format | カラム形式             | 列式格式              | -                          |
| Row Format      | 行形式                 | 行式格式              | -                          |
| Compression     | 圧縮                   | 壓縮                  | -                          |
| Encoding        | エンコード             | 編碼                  | -                          |
| Serialization   | シリアライゼーション   | 序列化                | -                          |
| Deserialization | デシリアライゼーション | 反序列化              | -                          |

## Data Analytics

| English                | Japanese                 | Chinese (Traditional) | Notes                     |
| ---------------------- | ------------------------ | --------------------- | ------------------------- |
| Analytics              | 分析                     | 分析                  | -                         |
| Business Intelligence  | ビジネスインテリジェンス | 商業智慧              | BI                        |
| Data Analysis          | データ分析               | 資料分析              | -                         |
| Descriptive Analytics  | 記述的分析               | 描述性分析            | -                         |
| Diagnostic Analytics   | 診断的分析               | 診斷性分析            | -                         |
| Predictive Analytics   | 予測分析                 | 預測性分析            | -                         |
| Prescriptive Analytics | 処方的分析               | 規範性分析            | -                         |
| KPI                    | KPI                      | KPI                   | Key Performance Indicator |
| Metric                 | メトリクス               | 指標                  | -                         |
| Dashboard              | ダッシュボード           | 儀表板                | -                         |
| Report                 | レポート                 | 報表                  | -                         |
| Visualization          | 可視化                   | 視覺化                | Data visualization        |
| Chart                  | チャート                 | 圖表                  | -                         |
| Graph                  | グラフ                   | 圖形                  | -                         |
| Trend                  | トレンド                 | 趨勢                  | -                         |
| Pattern                | パターン                 | 模式                  | -                         |
| Insight                | インサイト               | 洞察                  | -                         |
| Correlation            | 相関                     | 相關性                | -                         |
| Causation              | 因果関係                 | 因果關係              | -                         |
| Outlier                | 外れ値                   | 異常值                | -                         |
| Distribution           | 分布                     | 分佈                  | Statistical distribution  |

## Data Governance & Quality

| English                | Japanese               | Chinese (Traditional) | Notes                               |
| ---------------------- | ---------------------- | --------------------- | ----------------------------------- |
| Data Governance        | データガバナンス       | 資料治理              | -                                   |
| Data Steward           | データスチュワード     | 資料管理員            | -                                   |
| Data Catalog           | データカタログ         | 資料目錄              | -                                   |
| Metadata               | メタデータ             | 詮釋資料              | -                                   |
| Data Dictionary        | データディクショナリ   | 資料字典              | -                                   |
| Data Lineage           | データリネージ         | 資料血緣              | -                                   |
| Data Provenance        | データプロビナンス     | 資料來源              | -                                   |
| Data Quality           | データ品質             | 資料品質              | -                                   |
| Data Profiling         | データプロファイリング | 資料剖析              | -                                   |
| Data Validation        | データ検証             | 資料驗證              | -                                   |
| Data Cleansing         | データクレンジング     | 資料清洗              | -                                   |
| Data Standardization   | データ標準化           | 資料標準化            | -                                   |
| Master Data            | マスターデータ         | 主資料                | -                                   |
| Master Data Management | マスターデータ管理     | 主資料管理            | MDM                                 |
| Reference Data         | 参照データ             | 參考資料              | -                                   |
| Data Privacy           | データプライバシー     | 資料隱私              | -                                   |
| Data Security          | データセキュリティ     | 資料安全              | -                                   |
| PII                    | PII                    | PII                   | Personally Identifiable Information |
| Anonymization          | 匿名化                 | 匿名化                | -                                   |
| Encryption             | 暗号化                 | 加密                  | -                                   |

## Performance & Optimization

| English            | Japanese           | Chinese (Traditional) | Notes                  |
| ------------------ | ------------------ | --------------------- | ---------------------- |
| Performance        | パフォーマンス     | 效能                  | -                      |
| Optimization       | 最適化             | 最佳化                | -                      |
| Query Optimization | クエリ最適化       | 查詢最佳化            | -                      |
| Index              | インデックス       | 索引                  | -                      |
| Indexing           | インデキシング     | 索引編制              | -                      |
| Cache              | キャッシュ         | 快取                  | -                      |
| Caching            | キャッシング       | 快取處理              | -                      |
| Partitioning       | パーティショニング | 分割                  | -                      |
| Sharding           | シャーディング     | 分片                  | -                      |
| Execution Plan     | 実行計画           | 執行計畫              | Query execution plan   |
| Statistics         | 統計情報           | 統計資訊              | Database statistics    |
| Cardinality        | カーディナリティ   | 基數                  | -                      |
| Selectivity        | 選択率             | 選擇性                | -                      |
| Throughput         | スループット       | 吞吐量                | -                      |
| Latency            | レイテンシ         | 延遲                  | -                      |
| Bottleneck         | ボトルネック       | 瓶頸                  | Performance bottleneck |
| Connection Pool    | コネクションプール | 連線池                | -                      |
| Load Balancing     | 負荷分散           | 負載平衡              | -                      |
| Scaling            | スケーリング       | 擴展                  | -                      |
| Horizontal Scaling | 水平スケーリング   | 水平擴展              | -                      |
| Vertical Scaling   | 垂直スケーリング   | 垂直擴展              | -                      |
