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
def m_execute_query(sql: str) -> str:
    """
    指定されたSQLをwatsonx.dataのPrestoエンジンで実行して結果を返す。
    SELECT文のみ実行可能。
    :param sql: 実行するSELECT文
    :returns: クエリの実行結果
    """
    # SELECT文以外は拒否
    if not sql.strip().upper().startswith("SELECT"):
        return "エラー: SELECT文のみ実行可能です。"

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
    cursor.execute(sql)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    if not rows:
        return "結果が0件でした。"

    # ヘッダー + データを文字列で返す
    result = " | ".join(columns) + "\n"
    result += "-" * len(result) + "\n"
    for row in rows:
        result += " | ".join(str(v) for v in row) + "\n"

    return result
