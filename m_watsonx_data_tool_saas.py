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
def m_get_server_metrics_summary_saas() -> str:
    """
    サーバーメトリクステーブルの件数を返す疎通確認用ツール（SaaS版）。
    :returns: サーバーメトリクステーブルのレコード件数
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
    cursor.execute("SELECT COUNT(*) FROM server_metrics")
    row = cursor.fetchone()
    return f"server_metricsテーブルのレコード数: {row[0]}"
