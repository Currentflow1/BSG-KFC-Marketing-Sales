from django.db import models

class Employee(models.Model):
  SEX_CHOICES = [
      ('M', 'Male'),
      ('F', 'Female'),
  ]
  employee_id = models.BigAutoField(primary_key=True)
  employee_name = models.CharField(max_length=255)
  employee_nickname = models.CharField(max_length=255, null=True)
  employee_group = models.CharField(max_length=255, null=True)
  employee_position = models.CharField(max_length=255, null=True)
  employee_birthdate = models.DateField()
  employee_hiredate = models.DateField()
  employee_sex = models.CharField(max_length=1, choices=SEX_CHOICES)
  employee_sss = models.CharField(max_length=20, null=True)
  employee_gsis = models.CharField(max_length=20, null=True)
  employeeActive = models.BooleanField(default=False)

  def __str__(self):
    return self.employee_name

  class Meta:
    ordering = ['employee_name']