from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from ibm_watsonx_orchestrate.run import connections
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType, ExpectedCredentials
import prestodb

@tool(
    permission=ToolPermission.READ_ONLY,
    expected_credentials=[ExpectedCredentials(
        app_id="M-watsonx_data-saas",
        type=ConnectionType.KEY_VALUE
    )]
)
def m_get_top3_cpu_servers_saas() -> str:
    """
    CPU使用率の平均が高いサーバーTop3を返す（SaaS版）。
    :returns: CPU使用率Top3のサーバーIDと平均CPU使用率
    """
    conn_info = connections.key_value("M-watsonx_data-saas")

    conn = prestodb.dbapi.connect(
        host=conn_info.get("host"),
        port=int(conn_info.get("port")),
        user=conn_info.get("username"),
        auth=prestodb.auth.BasicAuthentication(
            conn_info.get("username"),
            conn_info.get("password")
        ),
        catalog="iceberg_data",
        schema="it_operations",
        http_scheme=conn_info.get("http_scheme"),
    )

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
