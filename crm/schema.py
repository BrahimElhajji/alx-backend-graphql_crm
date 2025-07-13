import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.core.validators import RegexValidator
from django.db import transaction
from django.core.exceptions import ValidationError
from graphql import GraphQLError
import datetime
from graphene_django.filter import DjangoFilterConnectionField
from .filters import CustomerFilter, ProductFilter, OrderFilter


# Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "stock")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise GraphQLError("Email already exists.")

        if phone:
            phone_validator = RegexValidator(
                regex=r'^(\+\d{1,15}|\d{3}-\d{3}-\d{4})$',
                message="Invalid phone format. Use +1234567890 or 123-456-7890"
            )
            try:
                phone_validator(phone)
            except ValidationError as e:
                raise GraphQLError(e.messages[0])

        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully.")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customers = graphene.List(
            graphene.InputObjectType(
                "CustomerInput",
                name=graphene.String(required=True),
                email=graphene.String(required=True),
                phone=graphene.String(required=False),
            ),
            required=True
        )

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, customers):
        created_customers = []
        errors = []

        for index, c in enumerate(customers):
            name = c.get("name")
            email = c.get("email")
            phone = c.get("phone", None)

            if Customer.objects.filter(email=email).exists():
                errors.append(f"Row {index + 1}: Email '{email}' already exists.")
                continue

            if phone:
                validator = RegexValidator(
                    regex=r'^(\+\d{1,15}|\d{3}-\d{3}-\d{4})$',
                    message="Invalid phone format."
                )
                try:
                    validator(phone)
                except ValidationError:
                    errors.append(f"Row {index + 1}: Invalid phone '{phone}'.")
                    continue

            try:
                customer = Customer(name=name, email=email, phone=phone)
                customer.full_clean()
                customer.save()
                created_customers.append(customer)
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False, default_value=0)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock):
        if price <= 0:
            raise GraphQLError("Price must be positive.")
        if stock < 0:
            raise GraphQLError("Stock cannot be negative.")

        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime(required=False)

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise GraphQLError("Invalid customer ID.")

        if not product_ids:
            raise GraphQLError("At least one product must be selected.")

        products = []
        total = 0
        for pid in product_ids:
            try:
                product = Product.objects.get(id=pid)
                products.append(product)
                total += float(product.price)
            except Product.DoesNotExist:
                raise GraphQLError(f"Invalid product ID: {pid}")

        order = Order(customer=customer, order_date=order_date or datetime.datetime.now(), total_amount=total)
        order.save()
        order.products.set(products)

        return CreateOrder(order=order)

class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass

    updated_products = graphene.List(ProductType)
    success_message = graphene.String()

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_products = []

        for product in low_stock_products:
            product.stock += 10
            product.save()
            updated_products.append(product)

        return UpdateLowStockProducts(
            updated_products=updated_products,
            success_message="Stock updated for low-stock products."
        )

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()

class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter, order_by=graphene.List(of_type=graphene.String))
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter, order_by=graphene.List(of_type=graphene.String))
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter, order_by=graphene.List(of_type=graphene.String))

