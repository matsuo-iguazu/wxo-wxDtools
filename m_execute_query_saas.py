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
def m_execute_query_saas(sql: str) -> str:
    """
    指定されたSQLをwatsonx.dataのPrestoエンジンで実行して結果を返す（SaaS版）。
    SELECT文のみ実行可能。
    :param sql: 実行するSELECT文
    :returns: クエリの実行結果
    """
    if not sql.strip().upper().startswith("SELECT"):
        return "エラー: SELECT文のみ実行可能です。"

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
    cursor.execute(sql)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    if not rows:
        return "結果が0件でした。"

    result = " | ".join(columns) + "\n"
    result += "-" * len(result) + "\n"
    for row in rows:
        result += " | ".join(str(v) for v in row) + "\n"

    return result
