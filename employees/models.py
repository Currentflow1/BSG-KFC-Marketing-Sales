from django.db import models

class Employee(models.Model):
  SEX_CHOICES = [
      ('M', 'Male'),
      ('F', 'Female'),
  ]
  employee_id = models.BigAutoField(primary_key=True)
  employee_name = models.CharField(max_length=255, default='')
  employee_nickname = models.CharField(max_length=255, null=True, default='')
  employee_group = models.CharField(max_length=255, null=True, default='')
  employee_position = models.CharField(max_length=255, null=True, default='')
  employee_birthdate = models.DateField(default='')
  employee_hiredate = models.DateField(default='')  # renamed from employeeDate for clarity
  employee_sex = models.CharField(max_length=1, choices=SEX_CHOICES, default='')
  employee_sss = models.CharField(max_length=20, null=True, default='')
  employee_gsis = models.CharField(max_length=20, null=True, default='')
  employeeActive = models.BooleanField(default=True)

  def __str__(self):
    return self.employee_name

  class Meta:
    ordering = ['employee_name']