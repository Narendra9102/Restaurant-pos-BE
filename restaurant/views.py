# restaurant/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction
from .models import Table, MenuItem, Order, OrderItem, Bill
from decimal import Decimal
import json


# ==================== TABLE MANAGEMENT ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_tables(request):
    """
    Get all tables with live status
    Requirement: Table Management - Show live dashboard
    Access: All roles can view
    """
    try:
        tables = Table.objects.all()
        
        tables_data = []
        for table in tables:
            tables_data.append({
                'id': table.id,
                'table_number': table.table_number,
                'seating_capacity': table.seating_capacity,
                'status': table.status,
                'created_at': table.created_at,
            })
        
        return Response({
            'success': True,
            'data': tables_data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_table(request):
    """
    Create new table
    Requirement: Table Management - CRUD tables
    Access: Manager only (RBAC requirement)
    """
    try:
        # Check if user is Manager
        if request.user.profile.role_id != 2:
            return Response({
                'success': False,
                'message': 'Only Manager can create tables'
            }, status=403)
        
        table_number = request.data.get('table_number')
        seating_capacity = request.data.get('seating_capacity')
        
        if not table_number or not seating_capacity:
            return Response({
                'success': False,
                'message': 'Table number and seating capacity required'
            }, status=400)
        
        # Check if table number exists
        if Table.objects.filter(table_number=table_number).exists():
            return Response({
                'success': False,
                'message': 'Table number already exists'
            }, status=400)
        
        table = Table.objects.create(
            table_number=table_number,
            seating_capacity=seating_capacity,
            status='Available'
        )
        
        return Response({
            'success': True,
            'message': 'Table created successfully',
            'data': {
                'id': table.id,
                'table_number': table.table_number,
                'seating_capacity': table.seating_capacity,
                'status': table.status
            }
        }, status=201)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_table(request, table_id):
    """
    Update table
    Access: Manager only
    """
    try:
        if request.user.profile.role_id != 2:
            return Response({
                'success': False,
                'message': 'Only Manager can update tables'
            }, status=403)
        
        table = Table.objects.get(id=table_id)
        
        table.table_number = request.data.get('table_number', table.table_number)
        table.seating_capacity = request.data.get('seating_capacity', table.seating_capacity)
        table.status = request.data.get('status', table.status)
        table.save()
        
        return Response({
            'success': True,
            'message': 'Table updated successfully'
        })
        
    except Table.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Table not found'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_table(request, table_id):
    """
    Delete table
    Access: Manager only
    """
    try:
        if request.user.profile.role_id != 2:
            return Response({
                'success': False,
                'message': 'Only Manager can delete tables'
            }, status=403)
        
        table = Table.objects.get(id=table_id)
        table_number = table.table_number
        table.delete()
        
        return Response({
            'success': True,
            'message': f'Table {table_number} deleted successfully'
        })
        
    except Table.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Table not found'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)


# ==================== MENU MANAGEMENT ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_menu_items(request):
    """
    Get all menu items (or only available ones)
    Access: All roles
    """
    try:
        # Waiter should only see available items
        if request.user.profile.role_id == 3:  # Waiter
            menu_items = MenuItem.objects.filter(is_available=True)
        else:
            menu_items = MenuItem.objects.all()
        
        items_data = []
        for item in menu_items:
            items_data.append({
                'id': item.id,
                'name': item.name,
                'category': item.category,
                'price': str(item.price),
                'is_available': item.is_available
            })
        
        return Response({
            'success': True,
            'data': items_data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_menu_item(request):
    """
    Create menu item
    Requirement: Manager CRUD menu
    Access: Manager only
    """
    try:
        if request.user.profile.role_id != 2:
            return Response({
                'success': False,
                'message': 'Only Manager can create menu items'
            }, status=403)
        
        name = request.data.get('name')
        category = request.data.get('category')
        price = request.data.get('price')
        is_available = request.data.get('is_available', True)
        
        if not name or not category or not price:
            return Response({
                'success': False,
                'message': 'Name, category, and price required'
            }, status=400)
        
        menu_item = MenuItem.objects.create(
            name=name,
            category=category,
            price=Decimal(price),
            is_available=is_available
        )
        
        return Response({
            'success': True,
            'message': 'Menu item created successfully',
            'data': {
                'id': menu_item.id,
                'name': menu_item.name,
                'category': menu_item.category,
                'price': str(menu_item.price),
                'is_available': menu_item.is_available
            }
        }, status=201)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_menu_item(request, item_id):
    """Update menu item - Manager only"""
    try:
        if request.user.profile.role_id != 2:
            return Response({
                'success': False,
                'message': 'Only Manager can update menu items'
            }, status=403)
        
        item = MenuItem.objects.get(id=item_id)
        
        item.name = request.data.get('name', item.name)
        item.category = request.data.get('category', item.category)
        item.price = Decimal(request.data.get('price', item.price))
        item.is_available = request.data.get('is_available', item.is_available)
        item.save()
        
        return Response({
            'success': True,
            'message': 'Menu item updated successfully'
        })
        
    except MenuItem.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Menu item not found'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_menu_item(request, item_id):
    """Delete menu item - Manager only"""
    try:
        if request.user.profile.role_id != 2:
            return Response({
                'success': False,
                'message': 'Only Manager can delete menu items'
            }, status=403)
        
        item = MenuItem.objects.get(id=item_id)
        item_name = item.name
        item.delete()
        
        return Response({
            'success': True,
            'message': f'Menu item {item_name} deleted successfully'
        })
        
    except MenuItem.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Menu item not found'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)


# ==================== ORDER MANAGEMENT ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """
    Create order with multiple items
    Requirement: Create orders, assign to table, add multiple menu items
    Access: Waiter only
    CRITICAL: Auto-change table status from Available to Occupied
    """
    try:
        # Check if user is Waiter
        if request.user.profile.role_id != 3:
            return Response({
                'success': False,
                'message': 'Only Waiter can create orders'
            }, status=403)
        
        table_id = request.data.get('table_id')
        items = request.data.get('items', [])  # [{menu_item_id, quantity}, ...]
        
        if not table_id or not items:
            return Response({
                'success': False,
                'message': 'Table and items required'
            }, status=400)
        
        table = Table.objects.get(id=table_id)
        
        # Create order with transaction
        with transaction.atomic():
            order = Order.objects.create(
                table=table,
                created_by=request.user,
                status='Placed'
            )
            
            # Create order items
            for item_data in items:
                menu_item = MenuItem.objects.get(id=item_data['menu_item_id'])
                quantity = item_data['quantity']
                
                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=quantity,
                    price_at_order=menu_item.price
                )
            
            # Calculate total
            order.calculate_total()
            
            # Signal will auto-change table status to Occupied
        
        return Response({
            'success': True,
            'message': 'Order created successfully',
            'data': {
                'order_id': order.id,
                'table': table.table_number,
                'status': order.status,
                'total_amount': str(order.total_amount)
            }
        }, status=201)
        
    except Table.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Table not found'
        }, status=404)
    except MenuItem.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Menu item not found'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    """
    Update order status (Placed → In Kitchen → Served)
    Requirement: Track order status
    Access: Waiter only
    """
    try:
        if request.user.profile.role_id != 3:
            return Response({
                'success': False,
                'message': 'Only Waiter can update order status'
            }, status=403)
        
        order = Order.objects.get(id=order_id)
        new_status = request.data.get('status')
        
        if new_status not in ['Placed', 'In Kitchen', 'Served']:
            return Response({
                'success': False,
                'message': 'Invalid status'
            }, status=400)
        
        order.status = new_status
        order.save()
        
        return Response({
            'success': True,
            'message': f'Order status updated to {new_status}'
        })
        
    except Order.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Order not found'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_table_orders(request, table_id):
    """Get all orders for a specific table"""
    try:
        table = Table.objects.get(id=table_id)
        orders = table.orders.all()
        
        orders_data = []
        for order in orders:
            items_data = []
            for item in order.order_items.all():
                items_data.append({
                    'menu_item': item.menu_item.name,
                    'quantity': item.quantity,
                    'price': str(item.price_at_order),
                    'subtotal': str(item.subtotal)
                })
            
            orders_data.append({
                'id': order.id,
                'status': order.status,
                'items': items_data,
                'total_amount': str(order.total_amount),
                'created_at': order.created_at
            })
        
        return Response({
            'success': True,
            'data': orders_data
        })
        
    except Table.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Table not found'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)


# ==================== BILLING ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_bill(request):
    """
    Generate bill for a table
    Requirement: Generate bill, show items, quantities, total, taxes
    Access: Cashier only
    """
    try:
        if request.user.profile.role_id != 4:
            return Response({
                'success': False,
                'message': 'Only Cashier can generate bills'
            }, status=403)
        
        table_id = request.data.get('table_id')
        
        if not table_id:
            return Response({
                'success': False,
                'message': 'Table ID required'
            }, status=400)
        
        table = Table.objects.get(id=table_id)
        
        # Check if table has orders
        orders = table.orders.filter(status='Served')
        if not orders.exists():
            return Response({
                'success': False,
                'message': 'No served orders found for this table'
            }, status=400)
        
        # Create bill
        bill = Bill.objects.create(
            table=table,
            generated_by=request.user,
            status='Pending Payment'
        )
        
        # Calculate bill
        bill.calculate_bill()
        
        # Get all items for response
        items_data = []
        for order in orders:
            for item in order.order_items.all():
                items_data.append({
                    'name': item.menu_item.name,
                    'quantity': item.quantity,
                    'price': str(item.price_at_order),
                    'subtotal': str(item.subtotal)
                })
        
        return Response({
            'success': True,
            'message': 'Bill generated successfully',
            'data': {
                'bill_id': bill.id,
                'table': table.table_number,
                'items': items_data,
                'subtotal': str(bill.subtotal),
                'tax_percentage': str(bill.tax_percentage),
                'tax_amount': str(bill.tax_amount),
                'total_amount': str(bill.total_amount),
                'status': bill.status
            }
        }, status=201)
        
    except Table.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Table not found'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def mark_bill_paid(request, bill_id):
    """
    Mark bill as paid
    Requirement: Once Paid → Table becomes Available again
    Access: Cashier only
    CRITICAL: Auto-change table status to Available via signal
    """
    try:
        if request.user.profile.role_id != 4:
            return Response({
                'success': False,
                'message': 'Only Cashier can mark bills as paid'
            }, status=403)
        
        bill = Bill.objects.get(id=bill_id)
        
        bill.status = 'Paid'
        bill.paid_at = timezone.now()
        bill.save()
        
        # Signal will auto-change table status to Available
        
        return Response({
            'success': True,
            'message': 'Bill marked as paid. Table is now available.',
            'data': {
                'bill_id': bill.id,
                'table': bill.table.table_number,
                'table_status': bill.table.status,
                'paid_at': bill.paid_at
            }
        })
        
    except Bill.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Bill not found'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_bills(request):
    """Get all pending bills - Cashier access"""
    try:
        if request.user.profile.role_id != 4:
            return Response({
                'success': False,
                'message': 'Only Cashier can view bills'
            }, status=403)
        
        bills = Bill.objects.filter(status='Pending Payment')
        
        bills_data = []
        for bill in bills:
            bills_data.append({
                'id': bill.id,
                'table': bill.table.table_number,
                'subtotal': str(bill.subtotal),
                'tax_amount': str(bill.tax_amount),
                'total_amount': str(bill.total_amount),
                'status': bill.status,
                'generated_at': bill.generated_at
            })
        
        return Response({
            'success': True,
            'data': bills_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)
    
    