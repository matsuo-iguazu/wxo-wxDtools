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
def m_get_top3_cpu_servers() -> str:
    """
    CPU使用率の平均が高いサーバーTop3を返す。
    :returns: CPU使用率Top3のサーバーIDと平均CPU使用率
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
        SELECT server_id, ROUND(AVG(cpu_usage), 2) AS avg_cpu
        FROM server_metrics
        GROUP BY server_id
        ORDER BY avg_cpu DESC
        LIMIT 3
    """)
    rows = cursor.fetchall()
    result = "CPU使用率Top3サーバー:\n"
    for i, row in enumerate(rows, 1):
        result += f"{i}. {row[0]}: 平均CPU {row[1]}%\n"
    return result
