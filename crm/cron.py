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


def update_low_stock():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=False,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)

    mutation = gql("""
    mutation {
      updateLowStockProducts {
        updatedProducts {
          id
          name
          stock
        }
        successMessage
      }
    }
    """)

    try:
        result = client.execute(mutation)
        products = result["updateLowStockProducts"]["updatedProducts"]
        success_message = result["updateLowStockProducts"]["successMessage"]

        with open("/tmp/low_stock_updates_log.txt", "a") as f:
            f.write(f"{timestamp} - {success_message}\n")
            for product in products:
                f.write(f"Product: {product['name']} - New stock: {product['stock']}\n")

    except Exception as e:
        with open("/tmp/low_stock_updates_log.txt", "a") as f:
            f.write(f"{timestamp} - Error running update_low_stock: {str(e)}\n")
