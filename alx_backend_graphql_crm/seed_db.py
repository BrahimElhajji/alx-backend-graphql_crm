from crm.models import Customer, Product

Customer.objects.create(name="John Doe", email="john@example.com", phone="+1234567890")
Product.objects.create(name="Phone", price=299.99, stock=15)
Product.objects.create(name="Headphones", price=99.99, stock=30)

