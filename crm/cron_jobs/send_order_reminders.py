#!/usr/bin/env python3

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime, timedelta
import logging

# Configure logging
log_file = "/tmp/order_reminders_log.txt"
logging.basicConfig(filename=log_file, level=logging.INFO)

# GraphQL transport and client setup
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=False,
    retries=3,
)
client = Client(transport=transport, fetch_schema_from_transport=False)

# Calculate date 7 days ago
seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

# GraphQL query
query = gql(f"""
query {{
  allOrders(ordering: "-orderDate") {{
    edges {{
      node {{
        id
        orderDate
        customer {{
          email
        }}
      }}
    }}
  }}
}}
""")

try:
    response = client.execute(query)
    orders = response["allOrders"]["edges"]

    for order_edge in orders:
        order = order_edge["node"]
        order_date = order["orderDate"]
        order_id = order["id"]
        customer_email = order["customer"]["email"]

        # Only log orders within last 7 days
        if order_date >= seven_days_ago:
            log_msg = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Order ID: {order_id}, Email: {customer_email}"
            logging.info(log_msg)

    print("Order reminders processed!")

except Exception as e:
    logging.error(f"{datetime.now()} - Error: {str(e)}")
    print("Failed to process order reminders.")
