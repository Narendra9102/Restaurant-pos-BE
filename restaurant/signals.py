# restaurant/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Order, Bill


@receiver(post_save, sender=Order)
def update_table_status_on_order(sender, instance, created, **kwargs):
    """
    "Ensure if a table is Available → Order should auto-set it to Occupied"
    
    When an order is created, automatically change table status to Occupied
    """
    if created:  # Only on order creation
        table = instance.table
        if table.status == 'Available':
            table.status = 'Occupied'
            table.save()
            print(f"✅ Table {table.table_number} auto-changed to Occupied")


@receiver(post_save, sender=Bill)
def update_table_status_on_payment(sender, instance, **kwargs):
    """
    "Once Paid → Table becomes Available again"
    
    When bill is marked as paid, automatically change table status to Available
    """
    if instance.status == 'Paid' and instance.paid_at:
        table = instance.table
        if table.status != 'Available':
            table.status = 'Available'
            table.save()
            print(f"✅ Table {table.table_number} auto-changed to Available after payment")

