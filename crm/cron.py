import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    now = datetime.datetime.now()
    timestamp = now.strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive\n"

    # Log to file
    with open("/tmp/crm_heartbeat_log.txt", "a") as log_file:
        log_file.write(message)

    # Optional: GraphQL ping to /graphql
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=False,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)

        query = gql("{ hello }")
        response = client.execute(query)
        # Optionally log or print result
    except Exception as e:
        with open("/tmp/crm_heartbeat_log.txt", "a") as log_file:
            log_file.write(f"{timestamp} GraphQL ping failed: {str(e)}\n")
