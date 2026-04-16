# DevOps & Cloud Computing Terminology

## Overview

This glossary covers DevOps practices, cloud computing platforms, containerization, orchestration, CI/CD pipelines, infrastructure as code, and site reliability engineering. Use this for cloud architecture documentation, deployment guides, and infrastructure content.

## Core DevOps Concepts

| English                  | Japanese                     | Chinese (Traditional) | Notes                    |
| ------------------------ | ---------------------------- | --------------------- | ------------------------ |
| DevOps                   | DevOps                       | DevOps                | Development + Operations |
| Continuous Integration   | 継続的インテグレーション     | 持續整合              | CI                       |
| Continuous Delivery      | 継続的デリバリー             | 持續交付              | CD                       |
| Continuous Deployment    | 継続的デプロイメント         | 持續部署              | CD                       |
| CI/CD                    | CI/CD                        | CI/CD                 | Keep acronym             |
| Pipeline                 | パイプライン                 | 流水線                | CI/CD pipeline           |
| Automation               | 自動化                       | 自動化                | -                        |
| Infrastructure as Code   | Infrastructure as Code       | 基礎設施即程式碼      | IaC                      |
| Configuration Management | 構成管理                     | 組態管理              | -                        |
| Version Control          | バージョン管理               | 版本控制              | -                        |
| Build                    | ビルド                       | 建置                  | -                        |
| Deploy                   | デプロイ                     | 部署                  | -                        |
| Release                  | リリース                     | 發布                  | -                        |
| Rollback                 | ロールバック                 | 回滾                  | -                        |
| Blue-Green Deployment    | ブルーグリーンデプロイメント | 藍綠部署              | -                        |
| Canary Deployment        | カナリアデプロイメント       | 金絲雀部署            | -                        |
| Rolling Update           | ローリングアップデート       | 滾動更新              | -                        |
| Feature Flag             | フィーチャーフラグ           | 功能旗標              | -                        |
| Artifact                 | アーティファクト             | 製品                  | Build artifact           |
| Repository               | リポジトリ                   | 儲存庫                | Code or artifact repo    |

## Containerization

| English              | Japanese           | Chinese (Traditional) | Notes                |
| -------------------- | ------------------ | --------------------- | -------------------- |
| Container            | コンテナ           | 容器                  | -                    |
| Docker               | Docker             | Docker                | Keep as-is           |
| Image                | イメージ           | 映像檔                | Container image      |
| Dockerfile           | Dockerfile         | Dockerfile            | Keep as-is           |
| Registry             | レジストリ         | 註冊表                | Container registry   |
| Docker Hub           | Docker Hub         | Docker Hub            | Keep as-is           |
| Docker Compose       | Docker Compose     | Docker Compose        | Keep as-is           |
| Volume               | ボリューム         | 磁碟區                | -                    |
| Network              | ネットワーク       | 網路                  | -                    |
| Layer                | レイヤー           | 層                    | Image layer          |
| Tag                  | タグ               | 標籤                  | Image tag            |
| Pull                 | プル               | 拉取                  | Pull image           |
| Push                 | プッシュ           | 推送                  | Push image           |
| Run                  | 実行               | 執行                  | Run container        |
| Stop                 | 停止               | 停止                  | Stop container       |
| Build                | ビルド             | 建置                  | Build image          |
| Commit               | コミット           | 提交                  | Commit container     |
| Port Mapping         | ポートマッピング   | 連接埠對應            | -                    |
| Environment Variable | 環境変数           | 環境變數              | -                    |
| Entrypoint           | エントリーポイント | 進入點                | Container entrypoint |

## Kubernetes

| English                 | Japanese             | Chinese (Traditional) | Notes                 |
| ----------------------- | -------------------- | --------------------- | --------------------- |
| Kubernetes              | Kubernetes           | Kubernetes            | Often abbreviated k8s |
| Cluster                 | クラスタ             | 叢集                  | -                     |
| Node                    | ノード               | 節點                  | -                     |
| Pod                     | Pod                  | Pod                   | Keep as-is            |
| Deployment              | デプロイメント       | 部署                  | k8s deployment        |
| Service                 | サービス             | 服務                  | k8s service           |
| Namespace               | 名前空間             | 命名空間              | -                     |
| ConfigMap               | ConfigMap            | ConfigMap             | Keep as-is            |
| Secret                  | シークレット         | 密鑰                  | -                     |
| Ingress                 | Ingress              | Ingress               | Keep as-is            |
| Volume                  | ボリューム           | 磁碟區                | -                     |
| Persistent Volume       | 永続ボリューム       | 持久卷                | PV                    |
| Persistent Volume Claim | 永続ボリューム要求   | 持久卷申領            | PVC                   |
| StatefulSet             | StatefulSet          | StatefulSet           | Keep as-is            |
| DaemonSet               | DaemonSet            | DaemonSet             | Keep as-is            |
| Job                     | ジョブ               | 作業                  | -                     |
| CronJob                 | CronJob              | CronJob               | Keep as-is            |
| ReplicaSet              | ReplicaSet           | ReplicaSet            | Keep as-is            |
| Label                   | ラベル               | 標籤                  | -                     |
| Selector                | セレクター           | 選擇器                | -                     |
| Annotation              | アノテーション       | 註釋                  | -                     |
| Helm                    | Helm                 | Helm                  | Keep as-is            |
| Chart                   | チャート             | Chart                 | Helm chart            |
| Operator                | Operator             | Operator              | k8s operator          |
| Kubectl                 | Kubectl              | Kubectl               | Keep as-is            |
| Control Plane           | コントロールプレーン | 控制平面              | -                     |
| Worker Node             | ワーカーノード       | 工作節點              | -                     |

## Cloud Platforms

| English           | Japanese                   | Chinese (Traditional) | Notes                          |
| ----------------- | -------------------------- | --------------------- | ------------------------------ |
| Cloud Computing   | クラウドコンピューティング | 雲端運算              | -                              |
| Public Cloud      | パブリッククラウド         | 公有雲                | -                              |
| Private Cloud     | プライベートクラウド       | 私有雲                | -                              |
| Hybrid Cloud      | ハイブリッドクラウド       | 混合雲                | -                              |
| Multi-Cloud       | マルチクラウド             | 多雲                  | -                              |
| AWS               | AWS                        | AWS                   | Amazon Web Services            |
| Azure             | Azure                      | Azure                 | Microsoft Azure                |
| GCP               | GCP                        | GCP                   | Google Cloud Platform          |
| IaaS              | IaaS                       | IaaS                  | Infrastructure as a Service    |
| PaaS              | PaaS                       | PaaS                  | Platform as a Service          |
| SaaS              | SaaS                       | SaaS                  | Software as a Service          |
| FaaS              | FaaS                       | FaaS                  | Function as a Service          |
| Serverless        | サーバーレス               | 無伺服器              | -                              |
| Virtual Machine   | 仮想マシン                 | 虛擬機器              | VM                             |
| Instance          | インスタンス               | 執行個體              | Cloud instance                 |
| Region            | リージョン                 | 區域                  | Cloud region                   |
| Availability Zone | アベイラビリティゾーン     | 可用區                | AZ                             |
| VPC               | VPC                        | VPC                   | Virtual Private Cloud          |
| Subnet            | サブネット                 | 子網路                | -                              |
| Security Group    | セキュリティグループ       | 安全群組              | -                              |
| IAM               | IAM                        | IAM                   | Identity and Access Management |
| S3                | S3                         | S3                    | Simple Storage Service         |
| EC2               | EC2                        | EC2                   | Elastic Compute Cloud          |
| Lambda            | Lambda                     | Lambda                | AWS Lambda                     |
| ECS               | ECS                        | ECS                   | Elastic Container Service      |
| EKS               | EKS                        | EKS                   | Elastic Kubernetes Service     |
| CloudFormation    | CloudFormation             | CloudFormation        | Keep as-is                     |
| Terraform         | Terraform                  | Terraform             | Keep as-is                     |

## Monitoring & Observability

| English                            | Japanese                           | Chinese (Traditional) | Notes                           |
| ---------------------------------- | ---------------------------------- | --------------------- | ------------------------------- |
| Monitoring                         | モニタリング                       | 監控                  | -                               |
| Observability                      | 可観測性                           | 可觀測性              | -                               |
| Metrics                            | メトリクス                         | 指標                  | -                               |
| Logs                               | ログ                               | 日誌                  | -                               |
| Traces                             | トレース                           | 追蹤                  | Distributed traces              |
| Alert                              | アラート                           | 警示                  | -                               |
| Dashboard                          | ダッシュボード                     | 儀表板                | -                               |
| Prometheus                         | Prometheus                         | Prometheus            | Keep as-is                      |
| Grafana                            | Grafana                            | Grafana               | Keep as-is                      |
| ELK Stack                          | ELKスタック                        | ELK堆疊               | Elasticsearch, Logstash, Kibana |
| Application Performance Monitoring | アプリケーションパフォーマンス監視 | 應用程式效能監控      | APM                             |
| Distributed Tracing                | 分散トレーシング                   | 分散式追蹤            | -                               |
| Service Mesh                       | サービスメッシュ                   | 服務網格              | -                               |
| Istio                              | Istio                              | Istio                 | Keep as-is                      |
| Linkerd                            | Linkerd                            | Linkerd               | Keep as-is                      |
| OpenTelemetry                      | OpenTelemetry                      | OpenTelemetry         | Keep as-is                      |
| Health Check                       | ヘルスチェック                     | 健康檢查              | -                               |
| Uptime                             | 稼働時間                           | 運作時間              | -                               |
| Downtime                           | ダウンタイム                       | 停機時間              | -                               |
| SLA                                | SLA                                | SLA                   | Service Level Agreement         |
| SLO                                | SLO                                | SLO                   | Service Level Objective         |
| SLI                                | SLI                                | SLI                   | Service Level Indicator         |

## Infrastructure & Networking

| English        | Japanese             | Chinese (Traditional) | Notes                                           |
| -------------- | -------------------- | --------------------- | ----------------------------------------------- |
| Infrastructure | インフラストラクチャ | 基礎設施              | -                                               |
| Network        | ネットワーク         | 網路                  | -                                               |
| Load Balancer  | ロードバランサー     | 負載平衡器            | -                                               |
| Reverse Proxy  | リバースプロキシ     | 反向代理              | -                                               |
| Firewall       | ファイアウォール     | 防火牆                | -                                               |
| VPN            | VPN                  | VPN                   | Virtual Private Network                         |
| DNS            | DNS                  | DNS                   | Domain Name System                              |
| CDN            | CDN                  | CDN                   | Content Delivery Network                        |
| IP Address     | IPアドレス           | IP位址                | -                                               |
| Port           | ポート               | 連接埠                | Network port                                    |
| Protocol       | プロトコル           | 協定                  | -                                               |
| TCP            | TCP                  | TCP                   | Transmission Control Protocol                   |
| UDP            | UDP                  | UDP                   | User Datagram Protocol                          |
| HTTP/HTTPS     | HTTP/HTTPS           | HTTP/HTTPS            | -                                               |
| SSL/TLS        | SSL/TLS              | SSL/TLS               | Secure Sockets Layer / Transport Layer Security |
| Certificate    | 証明書               | 憑證                  | SSL certificate                                 |
| Gateway        | ゲートウェイ         | 閘道                  | -                                               |
| Router         | ルーター             | 路由器                | -                                               |
| Switch         | スイッチ             | 交換器                | Network switch                                  |
| Bandwidth      | 帯域幅               | 頻寬                  | -                                               |
| Latency        | レイテンシ           | 延遲                  | -                                               |
| Throughput     | スループット         | 吞吐量                | -                                               |
| NAT            | NAT                  | NAT                   | Network Address Translation                     |

## Scaling & Performance

| English            | Japanese             | Chinese (Traditional) | Notes            |
| ------------------ | -------------------- | --------------------- | ---------------- |
| Scalability        | スケーラビリティ     | 可擴展性              | -                |
| Scaling            | スケーリング         | 擴展                  | -                |
| Horizontal Scaling | 水平スケーリング     | 水平擴展              | Scale out        |
| Vertical Scaling   | 垂直スケーリング     | 垂直擴展              | Scale up         |
| Auto Scaling       | オートスケーリング   | 自動擴展              | -                |
| Load Balancing     | 負荷分散             | 負載平衡              | -                |
| High Availability  | 高可用性             | 高可用性              | HA               |
| Fault Tolerance    | 耐障害性             | 容錯                  | -                |
| Redundancy         | 冗長性               | 冗餘                  | -                |
| Failover           | フェイルオーバー     | 容錯移轉              | -                |
| Disaster Recovery  | 災害復旧             | 災難復原              | DR               |
| Backup             | バックアップ         | 備份                  | -                |
| Replication        | レプリケーション     | 複製                  | Data replication |
| Caching            | キャッシング         | 快取                  | -                |
| Rate Limiting      | レート制限           | 速率限制              | -                |
| Throttling         | スロットリング       | 節流                  | -                |
| Circuit Breaker    | サーキットブレーカー | 斷路器                | -                |
| Retry              | リトライ             | 重試                  | -                |
| Timeout            | タイムアウト         | 逾時                  | -                |
| Queue              | キュー               | 佇列                  | Message queue    |

## Security & Compliance

| English                   | Japanese                 | Chinese (Traditional) | Notes                         |
| ------------------------- | ------------------------ | --------------------- | ----------------------------- |
| Security                  | セキュリティ             | 安全性                | -                             |
| Authentication            | 認証                     | 認證                  | -                             |
| Authorization             | 認可                     | 授權                  | -                             |
| Encryption                | 暗号化                   | 加密                  | -                             |
| Decryption                | 復号化                   | 解密                  | -                             |
| Certificate               | 証明書                   | 憑證                  | -                             |
| Key                       | 鍵                       | 金鑰                  | Encryption key                |
| Secret                    | シークレット             | 密鑰                  | Secret value                  |
| Token                     | トークン                 | 權杖                  | -                             |
| API Key                   | APIキー                  | API金鑰               | -                             |
| Access Control            | アクセス制御             | 存取控制              | -                             |
| Role-Based Access Control | ロールベースアクセス制御 | 角色型存取控制        | RBAC                          |
| Permission                | 権限                     | 權限                  | -                             |
| Policy                    | ポリシー                 | 政策                  | Security policy               |
| Vulnerability             | 脆弱性                   | 漏洞                  | -                             |
| Patch                     | パッチ                   | 修補程式              | Security patch                |
| Compliance                | コンプライアンス         | 合規                  | -                             |
| Audit                     | 監査                     | 稽核                  | Security audit                |
| Penetration Test          | ペネトレーションテスト   | 滲透測試              | -                             |
| Firewall                  | ファイアウォール         | 防火牆                | -                             |
| DDoS                      | DDoS                     | DDoS                  | Distributed Denial of Service |
| Intrusion Detection       | 侵入検知                 | 入侵偵測              | IDS                           |
| WAF                       | WAF                      | WAF                   | Web Application Firewall      |

## Site Reliability Engineering

| English                      | Japanese                               | Chinese (Traditional) | Notes                  |
| ---------------------------- | -------------------------------------- | --------------------- | ---------------------- |
| Site Reliability Engineering | サイトリライアビリティエンジニアリング | 網站可靠性工程        | SRE                    |
| Reliability                  | 信頼性                                 | 可靠性                | -                      |
| Availability                 | 可用性                                 | 可用性                | -                      |
| Uptime                       | 稼働時間                               | 運作時間              | -                      |
| Incident                     | インシデント                           | 事件                  | -                      |
| Incident Response            | インシデント対応                       | 事件回應              | -                      |
| Post-Mortem                  | 事後分析                               | 事後檢討              | -                      |
| Root Cause Analysis          | 根本原因分析                           | 根因分析              | RCA                    |
| On-Call                      | オンコール                             | 待命                  | -                      |
| Runbook                      | ランブック                             | 操作手冊              | -                      |
| Playbook                     | プレイブック                           | 腳本                  | Incident playbook      |
| Toil                         | トイル                                 | 瑣事                  | Repetitive manual work |
| Error Budget                 | エラーバジェット                       | 錯誤預算              | -                      |
| Change Management            | 変更管理                               | 變更管理              | -                      |
| Capacity Planning            | キャパシティプランニング               | 容量規劃              | -                      |
| Performance Tuning           | パフォーマンスチューニング             | 效能調校              | -                      |
