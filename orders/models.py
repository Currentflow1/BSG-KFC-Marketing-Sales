from django.db import models
from area_prices.models import Area
from customers.models import Customer
from employees.models import Employee
from products.models import Product


# OrderDetails Table
class OrderDetails(models.Model):
  od_id = models.BigAutoField(primary_key=True)
  od_control_no = models.CharField(max_length=15)
  od_area = models.ForeignKey(Area, on_delete=models.CASCADE)
  od_agent = models.ForeignKey(Employee, on_delete=models.CASCADE)
  od_van_number = models.IntegerField(null=True)
  od_beg_date = models.DateTimeField(auto_now_add=True)
  od_end_date = models.DateTimeField(null=True)


  def __str__(self):
    return str(self.od_control_no)

# CustomerDetails Table
class CustomerDetails(models.Model):
  cd_id = models.BigAutoField(primary_key=True)
  cd_control_no = models.ForeignKey(OrderDetails, on_delete=models.CASCADE)
  cd_invoice_no = models.IntegerField()
  cd_customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

  def __str__(self):
    return str(self.cd_invoice_no)


# DeliveryDetails Table
class DeliveryDetails(models.Model):
  order_type_choices = [
      ('MLOAD', 'MLOAD'),
      ('MRET', 'MRET'),
      ('VBO', 'VBO'),
  ]

  dd_id = models.BigAutoField(primary_key=True)
  dd_control_no = models.ForeignKey(OrderDetails, on_delete=models.CASCADE)
  dd_order_type = models.CharField(max_length=10, choices=order_type_choices)
  dd_product_code = models.ForeignKey(Product, on_delete=models.CASCADE)
  dd_quantity = models.IntegerField()
  dd_line_price = models.DecimalField(max_digits=20, decimal_places=2)


  def __str__(self):
    return f"{self.dd_control_no} - {self.dd_product_code} ({self.dd_order_type})"


# TransactionDetails Table
class TransactionDetails(models.Model):
  order_type_choices = [
    ('SO', 'SO'),
    ('SAM', 'SAM'),
    ('CRET', 'CRET'),
    ('CBO', 'CBO'),
  ]

  td_id = models.BigAutoField(primary_key=True)
  td_invoice_no = models.ForeignKey(CustomerDetails, on_delete=models.CASCADE)
  td_order_type = models.CharField(max_length=10, choices=order_type_choices)
  td_product_code = models.ForeignKey(Product, on_delete=models.CASCADE)
  td_quantity = models.IntegerField()
  td_line_price = models.DecimalField(max_digits=20, decimal_places=2)


  def __str__(self):
    return f"{self.td_invoice_no} - {self.td_product_code} ({self.td_order_type})"

# MarketingDetails Table
class MarketingDetails(models.Model):
  md_id = models.BigAutoField(primary_key=True)
  md_control_no = models.ForeignKey(OrderDetails, on_delete=models.CASCADE)
  md_total_SO = models.IntegerField()
  md_total_SAM = models.IntegerField()
  md_total_CRET = models.IntegerField()
  md_total_CBO = models.IntegerField()
  md_total_MLOAD = models.IntegerField()
  md_total_MRET = models.IntegerField()
  md_total_VBO = models.IntegerField()
  
  def __str__(self):
    return str(self.md_control_no)
