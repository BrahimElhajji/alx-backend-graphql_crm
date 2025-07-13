#!/bin/bash

# Activate your virtualenv if needed here (optional)
# source /path/to/your/venv/bin/activate

# Run Django shell command to delete customers with no orders since 1 year ago
DELETED_COUNT=$(python manage.py shell -c "
from django.utils.timezone import now, timedelta
from crm.models import Customer, Order

one_year_ago = now() - timedelta(days=365)
# Assuming Customer and Order have a relation where Order has customer FK
inactive_customers = Customer.objects.filter(order__date__lt=one_year_ago).distinct()
count = inactive_customers.count()
inactive_customers.delete()
print(count)
")

# Log the result with timestamp
echo \"\$(date '+%Y-%m-%d %H:%M:%S') - Deleted customers: \$DELETED_COUNT\" >> /tmp/customer_cleanup_log.txt
