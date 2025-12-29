# restaurant/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Table(models.Model):
    """
    Represents a restaurant table
    Requirement: Table Management (Section 1)
    """
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Occupied', 'Occupied'),
        ('Bill Requested', 'Bill Requested'),
        ('Closed', 'Closed'),
    ]
    
    table_number = models.CharField(max_length=10, unique=True)
    seating_capacity = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tables'
        ordering = ['table_number']
    
    def __str__(self):
        return f"{self.table_number} - {self.status}"


class MenuItem(models.Model):
    """
    Represents menu items available for ordering
    Requirement: Menu & Orders (Section 2)
    """
    CATEGORY_CHOICES = [
        ('Starter', 'Starter'),
        ('Main', 'Main'),
        ('Drinks', 'Drinks'),
        ('Dessert', 'Dessert'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'menu_items'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} - ₹{self.price}"


class Order(models.Model):
    """
    Represents an order placed at a table
    Requirement: Menu & Orders (Section 2)
    """
    STATUS_CHOICES = [
        ('Placed', 'Placed'),
        ('In Kitchen', 'In Kitchen'),
        ('Served', 'Served'),
    ]
    
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Placed')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders_created')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - {self.table.table_number}"
    
    def calculate_total(self):
        """Calculate total amount from order items"""
        total = sum(item.subtotal for item in self.order_items.all())
        self.total_amount = total
        self.save()
        return total


class OrderItem(models.Model):
    """
    Represents individual items in an order
    Requirement: Menu & Orders (Section 2) - Allow quantity change
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)  # Store price at time of order
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order_items'
    
    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate subtotal before saving"""
        if not self.price_at_order:
            self.price_at_order = self.menu_item.price
        self.subtotal = self.price_at_order * self.quantity
        super().save(*args, **kwargs)


class Bill(models.Model):
    """
    Represents a bill generated for a table
    Requirement: Billing (Section 3)
    """
    STATUS_CHOICES = [
        ('Not Generated', 'Not Generated'),
        ('Pending Payment', 'Pending Payment'),
        ('Paid', 'Paid'),
    ]
    
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='bills')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)  # 5% tax
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending Payment')
    generated_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='bills_generated')
    
    class Meta:
        db_table = 'bills'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"Bill #{self.id} - {self.table.table_number} - ₹{self.total_amount}"
    
    def calculate_bill(self):
        """
        Calculate bill from all orders of the table
        Requirement: Billing (Section 3) - Show items, quantities, total, taxes
        """
        # Get all orders for this table that are served
        orders = self.table.orders.filter(status='Served')
        
        # Calculate subtotal from all order items
        self.subtotal = sum(
            order_item.subtotal 
            for order in orders 
            for order_item in order.order_items.all()
        )
        
        # Calculate tax
        self.tax_amount = (self.subtotal * self.tax_percentage) / 100
        
        # Calculate total
        self.total_amount = self.subtotal + self.tax_amount
        
        self.save()
        return self.total_amount
    
    