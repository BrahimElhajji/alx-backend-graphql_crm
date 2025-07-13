#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Change to the Django project root (where manage.py is)
cd "$PROJECT_ROOT"

# Optional: activate virtualenv if needed
# source venv/bin/activate

# Run the Django cleanup logic
DELETED_COUNT=$(python manage.py shell -c "
from django.utils.timezone import now, timedelta
from crm.models import Customer
from crm.models import Order

one_year_ago = now() - timedelta(days=365)
inactive_customers = Customer.objects.exclude(order__created_at__gte=one_year_ago)
count = inactive_customers.count()
inactive_customers.delete()
print(count)
")

# Log the result with a timestamp
if [ $? -eq 0 ]; then
    echo \"\$(date '+%Y-%m-%d %H:%M:%S') - Deleted customers: \$DELETED_COUNT\" >> /tmp/customer_cleanup_log.txt
else
    echo \"\$(date '+%Y-%m-%d %H:%M:%S') - Cleanup failed\" >> /tmp/customer_cleanup_log.txt
fi
