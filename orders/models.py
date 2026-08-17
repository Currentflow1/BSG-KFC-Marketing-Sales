from django.db import models, transaction
from django.core.exceptions import ValidationError
from area_prices.models import Area, AreaPrice
from customers.models import Customer
from employees.models import Employee
from products.models import Product

CONTROL_NO_START = 30000

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
        on_delete=models.PROTECT,
        related_name="orders"
    )

    agent = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="orders"
    )

    beg_date = models.DateField(auto_now_add=True)
    mload_date = models.DateField(null=True, blank=True)
    mret_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OrderQuerySet.as_manager()

    class Meta:
        ordering = ["-beg_date"]

    @property
    def is_complete(self):
        return self.end_date is not None

    def clean(self):
        if self.end_date and self.end_date < self.beg_date:
            raise ValidationError(
                "End date cannot be earlier than begin date."
            )

    @classmethod
    def _generate_control_no(cls):
        with transaction.atomic():
            last = (
                cls.objects
                .select_for_update()
                .exclude(control_no="")
                .extra(select={"control_no_int": "CAST(control_no AS INTEGER)"})
                .order_by("-control_no_int")
                .first()
            )

            if last and last.control_no.isdigit():
                next_no = max(int(last.control_no) + 1, CONTROL_NO_START)
            else:
                next_no = CONTROL_NO_START

            return str(next_no)

    def save(self, *args, **kwargs):
        if not self.control_no:
            self.control_no = self._generate_control_no()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.control_no


class CustomerDetails(models.Model):
    id = models.BigAutoField(primary_key=True)

    order = models.ForeignKey(
        OrderDetails,
        on_delete=models.PROTECT,
        related_name="customers"
    )

    invoice_no = models.IntegerField(unique=True)

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="customer_details"
    )

    invoice_balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
    )

    @property
    def total_so_sam_price(self):
        result = self.transactions.filter( # type: ignore
            order_type__in=["SO", "SAM"]
        ).aggregate(total=models.Sum("line_price"))

        return result["total"] or 0

    @property
    def latest_so_sam_transaction(self):
        return self.transactions.filter( # type: ignore
            order_type__in=["SO", "SAM"]
        ).order_by("-created_at").first()

    def __str__(self):
        return str(self.invoice_no)


class DeliveryDetail(models.Model):
    ORDER_TYPE_CHOICES = [
        ("MLOAD", "MLOAD"),
        ("MRET", "MRET (-)"),
        ("VBO", "VBO (-)"),
    ]

    id = models.BigAutoField(primary_key=True)

    order = models.ForeignKey(
        OrderDetails,
        on_delete=models.PROTECT,
        related_name="deliveries"
    )

    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="delivery_lines"
    )

    quantity = models.PositiveIntegerField()
    line_price = models.DecimalField(max_digits=20, decimal_places=2)
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
        CustomerDetails,
        on_delete=models.PROTECT,
        related_name="transactions"
    )

    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES)
    invoice_type = models.CharField(max_length=10, choices=INVOICE_TYPE_CHOICES, blank=True)

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="transaction_lines"
    )
    quantity = models.PositiveIntegerField()
    line_price = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_detail} - {self.product} ({self.order_type})"


class MarketingDetails(models.Model):
    id = models.BigAutoField(primary_key=True)

    order = models.ForeignKey(
        OrderDetails,
        on_delete=models.PROTECT,
        related_name="marketing"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="marketing"
    )
    total_SO = models.IntegerField(default=0)
    total_SAM = models.IntegerField(default=0)
    total_CBO = models.IntegerField(default=0)
    total_CRET = models.IntegerField(default=0)
    total_MLOAD = models.IntegerField(default=0)
    total_MRET = models.IntegerField(default=0)
    total_VBO = models.IntegerField(default=0)

    @property
    def area_price(self):
        try:
            return AreaPrice.objects.get(
                area_name=self.order.area,
                product_name=self.product
            ).area_price
        except AreaPrice.DoesNotExist:
            return 0

    @property
    def total_CRET_display(self):
        return self.total_CRET * -1

    @property
    def total_VBO_display(self):
        return self.total_VBO * -1

    @property
    def total_CBO_display(self):
        return self.total_CBO * -1

    @property
    def total_MRET_display(self):
        return self.total_MRET * -1

    @property
    def total_SO_price(self):
        return self.total_SO * self.area_price

    @property
    def total_CRET_price(self):
        return self.total_CRET_display * self.area_price

    @property
    def total_SAM_price(self):
        return self.total_SAM * self.area_price

    @property
    def total_bo_price(self):
        return self.total_bo * self.area_price

    @property
    def total_VBO_price(self):
        return self.total_VBO_display * self.area_price

    @property
    def total_CBO_price(self):
        return self.total_CBO_display * self.area_price

    @property
    def total_MLOAD_price(self):
        return self.total_MLOAD * self.area_price

    @property
    def total_MRET_price(self):
        return self.total_MRET_display * self.area_price

    @property
    def total_short_over_price(self):
        return self.total_short_over_balance * self.area_price

    @property
    def total_BO_percentage(self):
        if self.total_MLOAD == 0:
            return 0

        return (self.total_VBO_display / self.total_MLOAD) * 100

    @property
    def total_out(self):
        return self.total_SO + self.total_SAM

    @property
    def total_total(self):
        return self.total_out + (-(self.total_MRET))

    @property
    def total_short_over_balance(self):
        return self.total_total - self.total_MLOAD

    @property
    def total_bo(self):
        return self.total_CBO - self.total_VBO

    def __str__(self):
        return f"{self.order.control_no} - {self.product.product_name}"

    @property
    def net_qty(self):
        return self.total_SO - self.total_CBO_display
 
    @property
    def net_price(self):
        return self.total_SO_price - self.total_CBO_price