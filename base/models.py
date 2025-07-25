from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# -------------------------------
# Inventory Module
# -------------------------------

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_available = models.BooleanField(default=True, blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    created_by = models.ForeignKey(
        'auth.User', 
        related_name='created_products',
        on_delete=models.SET_NULL,
        null=True
    )
    updated_by = models.ForeignKey(
        'auth.User', 
        related_name='updated_products',
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return self.name

class InventoryTransaction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_change = models.IntegerField()
    reason = models.CharField(max_length=100)  
    timestamp = models.DateTimeField(auto_now_add=True)

# -------------------------------
# Financial Module
# -------------------------------

class FinancialTransaction(models.Model):
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    module = models.CharField(max_length=50)  # e.g. Sales, HRM, Inventory
    timestamp = models.DateTimeField(auto_now_add=True)

# -------------------------------
# HRM Module
# -------------------------------

class Employee(models.Model):
    ROLE_CHOICES = [
        ('HR', 'HR'),
        ('FINANCE', 'Finance'),
        ('SALES', 'Sales'),
        ('ADMIN', 'Administrator'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    profile_picture = models.ImageField(upload_to='employee_profiles/', blank=True, null=True)


    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

class Payroll(models.Model):
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Cancelled', 'Cancelled'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0,  blank=True, null=True)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0,  blank=True, null=True)
    net_pay = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    pay_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.employee.name} - {self.pay_date}"
    

class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# -------------------------------
# Sales Module
# -------------------------------

class SalesOrder(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    shipping_address = models.TextField(blank=True, null=True)








# -------------------------------
# Manufacturing Module
# -------------------------------

class ManufacturingOrder(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_produced = models.PositiveIntegerField()
    raw_materials_used = models.ManyToManyField(Product, related_name='used_in_manufacturing')
    labor_hours = models.DecimalField(max_digits=5, decimal_places=2)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    production_date = models.DateField()

# -------------------------------
# Service Module
# -------------------------------

class ServiceRecord(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service_date = models.DateField()
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    parts_used = models.ManyToManyField(Product, blank=True)
    amount_billed = models.DecimalField(max_digits=10, decimal_places=2)
