# accounts/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile
from django.db import transaction


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_user(request):
    """
    Create new user (Manager, Waiter, Cashier)
    Only Admin (role_id=1) and Manager (role_id=2) can create users
    """
    try:
        # Get current user's role
        current_user = request.user
        current_role = current_user.profile.role_id

        print("=== CREATE USER DEBUG ===")
        print("Current user:", current_user.username)
        print("Current role:", current_role, type(current_role))

        
        # Get data from request
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        phone = request.data.get('phone', '')
        role_id = request.data.get('role_id')

        print("Requested role_id (raw):", role_id, type(role_id))
        try:
            role_id = int(role_id)
        except (TypeError, ValueError):
            return Response({'message': 'Invalid role_id'}, status=400)
        print("Requested role_id (int):", role_id, type(role_id))

        
        # Validation
        if not username or not password or not role_id:
            return Response({
                'success': False,
                'message': 'Username, password, and role are required'
            }, status=400)
        
        # Check permissions
        print("Permission check:")
        print("Current role:", current_role)
        print("Trying to create role:", role_id)

        if current_role == 1:  # Admin can create anyone
            if role_id not in [1, 2, 3, 4]:
                return Response({
                    'success': False,
                    'message': 'Invalid role_id'
                }, status=400)
        elif current_role == 2:  # Manager can only create Waiter and Cashier
            if role_id not in [3, 4]:
                return Response({
                    'success': False,
                    'message': 'Managers can only create Waiter and Cashier accounts'
                }, status=403)
        else:  # Waiter and Cashier cannot create users
            return Response({
                'success': False,
                'message': 'You do not have permission to create users'
            }, status=403)
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return Response({
                'success': False,
                'message': 'Username already exists'
            }, status=400)
        
        # Check if email already exists
        if email and User.objects.filter(email=email).exists():
            return Response({
                'success': False,
                'message': 'Email already exists'
            }, status=400)
        
        # Create user with transaction (all or nothing)
        with transaction.atomic():
            # Create User
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Set is_staff based on role
            if role_id == 2:  # Manager
                user.is_staff = True
            else:  # Waiter, Cashier
                user.is_staff = False
            
            user.save()
            
            # Update or create UserProfile
            profile, created = UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'role_id': role_id,
                    'phone': phone,
                    'created_by': current_user
                }
            )
        
        return Response({
            'success': True,
            'message': 'User created successfully',
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role_id': role_id,
                'role_name': profile.get_role_id_display(),
                'phone': phone
            }
        }, status=201)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error creating user: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users(request):
    """
    Get all users
    Only Admin and Manager can view users
    """
    try:
        current_role = request.user.profile.role_id
        
        # Check permissions
        if current_role not in [1, 2]:
            return Response({
                'success': False,
                'message': 'You do not have permission to view users'
            }, status=403)
        
        # Get all users with profiles
        users = User.objects.select_related('profile').all()
        
        users_data = []
        for user in users:
            try:
                users_data.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role_id': user.profile.role_id,
                    'role_name': user.profile.get_role_id_display(),
                    'phone': user.profile.phone,
                    'created_at': user.profile.created_at,
                    'is_active': user.is_active
                })
            except:
                continue
        
        return Response({
            'success': True,
            'data': users_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error fetching users: {str(e)}'
        }, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, user_id):
    """
    Delete user
    Only Admin can delete users
    """
    try:
        current_role = request.user.profile.role_id
        
        # Only Admin can delete
        if current_role != 1:
            return Response({
                'success': False,
                'message': 'Only Admin can delete users'
            }, status=403)
        
        # Get user
        user = User.objects.get(id=user_id)
        
        # Cannot delete yourself
        if user.id == request.user.id:
            return Response({
                'success': False,
                'message': 'Cannot delete your own account'
            }, status=400)
        
        username = user.username
        user.delete()
        
        return Response({
            'success': True,
            'message': f'User {username} deleted successfully'
        })
        
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error deleting user: {str(e)}'
        }, status=500)


@api_view(['POST'])
@permission_classes([])
def login_view(request):
    """
    Login API - returns JWT token and user info
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'success': False,
            'message': 'Username and password required'
        }, status=400)
    
    # Authenticate user
    user = authenticate(username=username, password=password)
    
    if user is not None:
        # Check if user has profile
        try:
            profile = user.profile
            role_id = profile.role_id
        except:
            return Response({
                'success': False,
                'message': 'User profile not found'
            }, status=400)
        
        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'role_id': role_id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        })
    else:
        return Response({
            'success': False,
            'message': 'Invalid username or password'
        }, status=401)
    

