"""
Seed data for Restaurant POS System

IMPORTANT:
1. First create Django superuser (Admin)
2. Admin should create Manager / Waiter / Cashier users via Admin panel or API
3. This file only seeds:
   - Tables
   - Menu Items

Run:
python manage.py shell
>>> exec(open("restaurant/seed_data.py").read())
"""

from decimal import Decimal
from restaurant.models import Table, MenuItem

print("🚀 Seeding Restaurant Data...")

# -----------------------------
# Create Tables
# -----------------------------
tables_data = [
    {"table_number": "T-01", "seating_capacity": 2},
    {"table_number": "T-02", "seating_capacity": 4},
    {"table_number": "T-03", "seating_capacity": 4},
    {"table_number": "T-04", "seating_capacity": 6},
]

for table in tables_data:
    obj, created = Table.objects.get_or_create(
        table_number=table["table_number"],
        defaults={
            "seating_capacity": table["seating_capacity"],
            "status": "Available",
        }
    )
    if created:
        print(f"✅ Created Table {obj.table_number}")
    else:
        print(f"⚠️ Table {obj.table_number} already exists")

# -----------------------------
# Create Menu Items
# -----------------------------
menu_items_data = [
    # Starters
    {"name": "Spring Rolls", "category": "Starter", "price": Decimal("120.00")},
    {"name": "Paneer Tikka", "category": "Starter", "price": Decimal("180.00")},

    # Main Course
    {"name": "Paneer Butter Masala", "category": "Main", "price": Decimal("250.00")},
    {"name": "Dal Makhani", "category": "Main", "price": Decimal("180.00")},
    {"name": "Veg Biryani", "category": "Main", "price": Decimal("220.00")},

    # Drinks
    {"name": "Soft Drink", "category": "Drinks", "price": Decimal("50.00")},
    {"name": "Mango Lassi", "category": "Drinks", "price": Decimal("80.00")},

    # Desserts
    {"name": "Ice Cream", "category": "Dessert", "price": Decimal("80.00")},
]

for item in menu_items_data:
    obj, created = MenuItem.objects.get_or_create(
        name=item["name"],
        defaults={
            "category": item["category"],
            "price": item["price"],
            "is_available": True,
        }
    )
    if created:
        print(f"✅ Created Menu Item: {obj.name}")
    else:
        print(f"⚠️ Menu Item already exists: {obj.name}")

print("🎉 Seed data completed successfully!")
