from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from ibm_watsonx_orchestrate.run import connections
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType, ExpectedCredentials
import prestodb
import requests
import urllib3
import os

# TechZone環境の自己署名証明書のため警告を抑制
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@tool(
    permission=ToolPermission.READ_ONLY,
    expected_credentials=[ExpectedCredentials(
        app_id="M-watsonx_data-test",
        type=ConnectionType.BASIC_AUTH
    )]
)
def m_get_server_metrics_summary() -> str:
    """
    サーバーメトリクステーブルの件数を返す疎通確認用ツール。
    :returns: サーバーメトリクステーブルのレコード件数
    """
    conn_info = connections.basic_auth("M-watsonx_data-test")

    # SSL検証をスキップするセッションを作成
    session = requests.Session()
    session.verify = False

    conn = prestodb.dbapi.connect(
        host="jp-tok.services.cloud.techzone.ibm.com",
        port=41970,
        user=conn_info.username,
        auth=prestodb.auth.BasicAuthentication(conn_info.username, conn_info.password),
        catalog="iceberg_data",
        schema="it_operations",
        http_scheme="https",
    )
    # セッションのverifyを上書き
    conn._http_session = session

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM server_metrics")
    row = cursor.fetchone()
    return f"server_metricsテーブルのレコード数: {row[0]}"
