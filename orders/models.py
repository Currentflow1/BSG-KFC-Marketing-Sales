from django.db import models
from area_prices.models import Area
from customers.models import Customer
from employees.models import Employee
from products.models import Product


class OrderQuerySet(models.QuerySet):
    def incomplete(self):
        return self.filter(end_date__isnull=True)

    def completed(self):
        return self.filter(end_date__isnull=False)

class OrderDetails(models.Model):
    id = models.BigAutoField(primary_key=True)

    control_no = models.CharField(max_length=15, unique=True)

    area = models.ForeignKey(
        Area,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    agent = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    van_number = models.IntegerField(null=True, blank=True)

    beg_date = models.DateField()
    mload_date = models.DateField(null=True, blank=True)
    mret_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    objects = OrderQuerySet.as_manager()

    class Meta:
        ordering = ["-beg_date"]

    @property
    def is_complete(self):
        return self.end_date is not None

class CustomerDetails(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(OrderDetails, on_delete=models.CASCADE, related_name="customers")
    invoice_no = models.IntegerField(unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="customer_details")

    def __str__(self):
        return str(self.invoice_no)


class DeliveryDetail(models.Model):
    ORDER_TYPE_CHOICES = [
        ("MLOAD", "MLOAD"),
        ("MRET", "MRET (-)"),
        ("VBO", "VBO (-)"),
    ]

    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(OrderDetails, on_delete=models.CASCADE, related_name="deliveries")
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="delivery_lines")
    quantity = models.IntegerField()
    line_price = models.DecimalField(max_digits=20, decimal_places=2)
    remarks = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order} - {self.product} ({self.order_type})"


class TransactionDetail(models.Model):
    ORDER_TYPE_CHOICES = [
        ("SO", "SO"),
        ("SAM", "SAM"),
        ("CRET", "CRET (-)"),
        ("CBO", "CBO (-)"),
    ]
    INVOICE_TYPE_CHOICES = [
        ("CASH", "Cash"),
        ("CHARGE", "Charge"),
        ("CHEQUE", "Cheque"),
    ]

    id = models.BigAutoField(primary_key=True)
    customer_detail = models.ForeignKey(
        CustomerDetails, on_delete=models.CASCADE, related_name="transactions"
    )
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES)
    invoice_type = models.CharField(max_length=10, choices=INVOICE_TYPE_CHOICES, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="transaction_lines")
    quantity = models.IntegerField()
    line_price = models.DecimalField(max_digits=20, decimal_places=2)
    remarks = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_detail} - {self.product} ({self.order_type})"
class MarketingDetails(models.Model):
    id = models.BigAutoField(primary_key=True)

    order = models.OneToOneField(
        OrderDetails,
        on_delete=models.CASCADE,
        related_name="marketing"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    total_SO = models.IntegerField(default=0)
    total_SAM = models.IntegerField(default=0)
    total_CBO = models.IntegerField(default=0)
    total_CRET = models.IntegerField(default=0)
    total_MLOAD = models.IntegerField(default=0)
    total_MRET = models.IntegerField(default=0)
    total_VBO = models.IntegerField(default=0)

    def __str__(self):
        return self.order.control_no