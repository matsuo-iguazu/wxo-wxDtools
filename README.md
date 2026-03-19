# watsonx Orchestrate × watsonx.data 連携サンプル

## 概要

本リポジトリは、watsonx Orchestrate (wxO) から watsonx.data (wxD) に接続する方法の**検証用**に作成した環境です。

wxD 上の Iceberg テーブルに格納されたデータが Presto エンジン経由でアクセスできるようになっており、
wxO のツール・接続（Connection）を使ってそのデータにアクセスするエージェントを構築します。
エージェントに自然言語で問い合わせることで、サーバーリソースのメトリクスデータを取得・分析できます。

### 検証環境

| 項目 | 内容 |
|------|------|
| wxO | IBM TechZone VM仮想環境版 |
| wxD | IBM TechZone VM仮想環境版 |
| クエリエンジン | Presto |
| テーブルフォーマット | Apache Iceberg |
| ストレージ | MinIO |

> **TechZone VM仮想環境について**  
> TechZone の VM 仮想環境版は自己署名SSL証明書を使用しているため、
> Presto への接続時に証明書検証のスキップが必要です。
> IBM Cloud SaaS版のwatsonx.dataではこの対応は不要です。

---

## 構成

```
wxo-wxDtools/
├── m_watsonx_data_tool.py    # 疎通確認用ツール
├── m_get_top3_cpu_servers.py # CPU使用率Top3取得ツール
├── m_get_server_stats.py     # サーバー統計情報取得ツール
├── m_execute_query.py        # 任意SQLを実行するツール（Text2SQL用）
├── requirements.txt          # Pythonライブラリ
├── presto_cert.pem           # SSL証明書（各自の環境のものを使用、Gitに含めない）
└── insert_server_metrics.sql # サンプルデータ投入SQL
```

## 前提条件

- IBM TechZone上のwatsonx.data環境（またはIBM Cloud上のwatsonx.data）
- watsonx Orchestrate（wxO）のアカウント
- wxO ADK（Agent Development Kit）のインストール済み環境
- Python 3.11以上

---

## Step 1: watsonx.data のセットアップ

### 1-1. スキーマの作成

watsonx.data コンソールを開き、左メニューから **データ・マネージャー** を選択します。
`iceberg_data` カタログの3点リーダーをクリックして「スキーマの作成」を選び、以下の名前で作成します。

```
it_operations
```

### 1-2. テーブルの作成

照会ワークスペースを開き、以下のSQLを実行します。

```sql
CREATE TABLE iceberg_data.it_operations.server_metrics (
    server_id    VARCHAR,
    timestamp    TIMESTAMP,
    cpu_usage    DECIMAL(5,2),
    memory_usage DECIMAL(5,2),
    disk_usage   DECIMAL(5,2),
    network_in   DECIMAL(10,2),
    network_out  DECIMAL(10,2)
)
WITH (
    format = 'PARQUET'
);
```

### 1-3. サンプルデータの投入

`insert_server_metrics.sql` の内容（4つのINSERT文で構成されています）を照会ワークスペースに貼り付けて、順番に実行してください。

投入後、以下のSQLで360件になっていることを確認します。

```sql
SELECT COUNT(*) FROM iceberg_data.it_operations.server_metrics;
```

#### サンプルデータのサーバー特性

| サーバーID | 特性 |
|-----------|------|
| srv-001 | 高負荷（CPU高め） |
| srv-002 | 正常 |
| srv-003 | メモリ逼迫 |
| srv-004 | 安定・低負荷 |
| srv-005 | 不安定（ばらつきあり） |

---

## Step 2: SSL証明書の取得

> ⚠️ **注意: TechZone VM仮想環境での手順です**  
> 以下はTechZone VM仮想環境固有の手順です。IBM Cloud SaaS版など他の環境を利用する場合は、
> ご利用の環境に合わせて変更してください。SaaS版の場合、この手順は不要です。

watsonx.data コンソールの **「エンジンとサービス接続の詳細」** から `presto-01` を展開し、
SSL証明書のテキストをコピーして `presto_cert.pem` として保存します。

```
-----BEGIN CERTIFICATE-----
（証明書テキスト）
-----END CERTIFICATE-----
```

---

## Step 3: wxO の Connection 設定

> ⚠️ **注意: TechZone VM仮想環境での手順です**  
> 以下のホスト名・ポートはTechZone VM仮想環境のものです。
> IBM Cloud SaaS版など他の環境を利用する場合は、ご利用の環境に合わせて変更してください。
> なお、UsernameとPasswordはPrestoの認証情報です（TechZoneのログイン情報とは異なります）。
> SaaS版など他環境での認証情報の取得方法は各環境のドキュメントを参照してください。

wxO のUIから以下の手順でConnectionを作成します。

1. wxO コンソール → **Connections** → 新規作成
2. 以下の内容で設定します

| 項目 | 値 |
|------|----|
| 接続名 | M-watsonx_data-test |
| 認証タイプ | Basic Auth |
| Server URL | `http://jp-tok.services.cloud.techzone.ibm.com:41970` |
| Username | PrestoのユーザーID |
| Password | Prestoのパスワード |

---

## Step 4: Pythonツールのインポート

### 4-1. 依存ライブラリのインストール

```bash
pip install presto-python-client
```

### 4-2. ツールのインポート

`wxo-wxDtools` ディレクトリに移動してから実行します。

```bash
cd wxo-wxDtools

# 疎通確認ツール
orchestrate tools import -k python \
  -f m_watsonx_data_tool.py \
  -p . \
  -r requirements.txt \
  --app-id M-watsonx_data-test

# CPU Top3ツール
orchestrate tools import -k python \
  -f m_get_top3_cpu_servers.py \
  -p . \
  -r requirements.txt \
  --app-id M-watsonx_data-test

# サーバー統計ツール
orchestrate tools import -k python \
  -f m_get_server_stats.py \
  -p . \
  -r requirements.txt \
  --app-id M-watsonx_data-test

# 任意SQL実行ツール
orchestrate tools import -k python \
  -f m_execute_query.py \
  -p . \
  -r requirements.txt \
  --app-id M-watsonx_data-test
```

---

## Step 5: エージェントの設定

wxO のUIからエージェントを作成し、以下のツールを追加します。

| ツール名 | 位置づけ | 入力 |
|---------|---------|------|
| `m_get_server_metrics_summary` | 疎通確認 | なし |
| `m_get_top3_cpu_servers` | 特定用途機能（CPU使用率Top3取得） | なし |
| `m_get_server_stats` | 特定用途機能（サーバー統計情報取得） | server_id |
| `m_execute_query` | 汎用SQL実行（Text2SQL用） | sql |

### エージェントのBehavior（動作定義）サンプル

`m_execute_query` ツールを使ったText2SQLを有効にするために、以下をエージェントのBehaviorに設定してください。

```
あなたはIT運用データを分析するエージェントです。
ユーザーからデータの問い合わせがあった場合、m_execute_queryツールを使ってSQLを実行し、結果を返してください。

## 利用可能なテーブル

### iceberg_data.it_operations.server_metrics
サーバーのリソース使用率を時系列で記録したテーブルです。

| カラム名 | 型 | 説明 |
|---------|-----|------|
| server_id | VARCHAR | サーバーID（例: srv-001〜srv-005） |
| timestamp | TIMESTAMP | 計測日時 |
| cpu_usage | DECIMAL(5,2) | CPU使用率（%） |
| memory_usage | DECIMAL(5,2) | メモリ使用率（%） |
| disk_usage | DECIMAL(5,2) | ディスク使用率（%） |
| network_in | DECIMAL(10,2) | 受信トラフィック（MB/s） |
| network_out | DECIMAL(10,2) | 送信トラフィック（MB/s） |

## ルール
- SQLはSELECT文のみ使用してください。
- テーブル名は必ず iceberg_data.it_operations.server_metrics を使用してください。
- カラム名は上記の定義に従ってください。
```

> **ツールの使い分けについて**  
> `m_get_top3_cpu_servers` と `m_execute_query` を同時に登録した場合、
> エージェントはツールの説明文を読んで適切な方を自律的に選択します。
> 「Top3ではなく全サーバーを見たい」などの場合は `m_execute_query` が選ばれます。

---

## 使い方の例

### 固定ツールを使った問い合わせ
```
CPU使用率が高いサーバーTop3を教えて
```
```
Top3の中で一番やばいサーバーの詳細も教えて
```
```
srv-001の統計情報を教えて
```

### Text2SQL（m_execute_queryツール）を使った問い合わせ
```
CPU使用率が高いサーバーを教えて、ただしTop3ではないよ
```
```
m_execute_queryを使って、全サーバーのメモリ使用率の平均を教えて
```

---

## 補足

### TechZone VM仮想環境固有のSSL設定について

TechZone VM仮想環境は自己署名SSL証明書を使用しているため、Pythonコード内で以下の対応をしています。

```python
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
session = requests.Session()
session.verify = False
conn._http_session = session
```

IBM Cloud SaaS版のwatsonx.dataに接続する場合は、CA署名済み証明書が使われているため
この部分は不要です。接続コードをシンプルにすることができます。

### .gitignore の設定

証明書ファイルはGitに含めないようにしてください。

```
# .gitignore
presto_cert.pem
```

### wxDへのアクセス方法の検討

wxDのPrestoにはREST API（`/v1/statement`）が用意されており、SQLを直接POSTすることができる。
ただし、Prestoのクライアントプロトコルは非同期のポーリング方式のため、OpenAPIツールとして定義することは難しい。

| アクセス方法 | 概要 | OpenAPIツール化 | 備考 |
|------------|------|----------------|------|
| **Pythonツール（採用）** | `prestodb` ライブラリがポーリングを隠蔽してくれるため、シンプルなコードでSQLを実行できる | 不要 | 本リポジトリで採用 |
| **OpenAPIツール** | PrestoのREST APIをOpenAPIで定義してwxOに登録する | ポーリングのロジックを表現できないため困難 | 薄いラッパーAPIサーバーを別途立てる必要あり |
| **Arrow Flight（将来の可能性）** | wxDが対応しているgRPCベースの高速データ転送プロトコル。ポーリング不要でバイナリ転送のため高効率 | gRPCベースのためOpenAPIには乗らない | 今後の発展として期待 |

現時点では `prestodb` ライブラリを使ったPythonツールが、最もシンプルで実用的なアクセス方法である。
