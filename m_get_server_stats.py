from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from ibm_watsonx_orchestrate.run import connections
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType, ExpectedCredentials
import prestodb
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@tool(
    permission=ToolPermission.READ_ONLY,
    expected_credentials=[ExpectedCredentials(
        app_id="M-watsonx_data-test",
        type=ConnectionType.BASIC_AUTH
    )]
)
def m_get_server_stats(server_id: str) -> str:
    """
    指定したサーバーのリソース統計情報（CPU・メモリ・ディスクの平均・最大・最小）を返す。
    :param server_id: サーバーID（例: srv-001）
    :returns: 指定サーバーのリソース統計情報
    """
    conn_info = connections.basic_auth("M-watsonx_data-test")

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
    conn._http_session = session

    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            ROUND(AVG(cpu_usage), 2)    AS avg_cpu,
            ROUND(MAX(cpu_usage), 2)    AS max_cpu,
            ROUND(MIN(cpu_usage), 2)    AS min_cpu,
            ROUND(AVG(memory_usage), 2) AS avg_mem,
            ROUND(MAX(memory_usage), 2) AS max_mem,
            ROUND(MIN(memory_usage), 2) AS min_mem,
            ROUND(AVG(disk_usage), 2)   AS avg_disk,
            ROUND(MAX(disk_usage), 2)   AS max_disk,
            ROUND(MIN(disk_usage), 2)   AS min_disk
        FROM server_metrics
        WHERE server_id = ?
    """, (server_id,))
    row = cursor.fetchone()
    if not row or row[0] is None:
        return f"サーバー {server_id} のデータが見つかりません。"

    return (
        f"=== {server_id} の統計情報 ===\n"
        f"CPU使用率    : 平均 {row[0]}% / 最大 {row[1]}% / 最小 {row[2]}%\n"
        f"メモリ使用率 : 平均 {row[3]}% / 最大 {row[4]}% / 最小 {row[5]}%\n"
        f"ディスク使用率: 平均 {row[6]}% / 最大 {row[7]}% / 最小 {row[8]}%\n"
    )
