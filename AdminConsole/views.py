from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from order_management.models import Return, Order, Payment, OrderItem
from UserAccounts.models import User
from user_pannel.models import UserAddress
from cart.models import Wallet, WalletTransaction
from products.models import Products, ProductVariant
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta, date
import json
from django.db import models  # Import models
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate  # Import TruncDate for date truncation
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.cache import never_cache
from order_management.models import Order, OrderItem  # Adjust the imports based on your app structure


def is_admin(user):
    return  user.is_admin


@user_passes_test(is_admin)
@never_cache
def admin_page(request):
    time_range = request.GET.get('time_range', 'weekly')

    if time_range == 'weekly':
        start_date = timezone.now() - timedelta(days=7)
    elif time_range == 'monthly':
        start_date = timezone.now() - timedelta(days=30)
    elif time_range == 'yearly':
        start_date = timezone.now() - timedelta(days=365)
    else:
        start_date = timezone.now() - timedelta(days=7)  

    orders = Order.objects.filter(created_at__gte=start_date)

    total_orders = orders.count()
    total_revenue = Order.objects.filter(created_at__gte=start_date).aggregate(Sum('final_price'))['final_price__sum'] or 0
    pending_orders = orders.filter(status='Pending').count()
    completed_orders = orders.filter(status='Delivered').count()

    order_trends = orders.annotate(date=TruncDate('created_at')) \
                         .values('date') \
                         .annotate(count=Count('id'), revenue=Sum('final_price')) \
                         .order_by('date')
    

    dates = [entry['date'].strftime('%Y-%m-%d') for entry in order_trends]
    orders_data = [entry['count'] for entry in order_trends]
    revenue_data = [float(entry['revenue']) for entry in order_trends]


    order_status_data = [
        orders.filter(status='Pending').count(),
        orders.filter(status='Processing').count(),
        orders.filter(status='Shipped').count(),
        orders.filter(status='Delivered').count()
    ]

# Get top 5 selling products
    top_products = OrderItem.objects.filter(order__created_at__gte=start_date) \
                                .values('product_variant__product__product_name') \
                                .annotate(total_quantity=Sum('quantity')) \
                                .order_by('-total_quantity')[:5]

# Get top 5 selling variants
    top_variants = OrderItem.objects.filter(order__created_at__gte=start_date) \
                                .values('product_variant__variant_name') \
                                .annotate(total_quantity=Sum('quantity')) \
                                .order_by('-total_quantity')[:5]
    top_brands = OrderItem.objects.filter(order__created_at__gte=start_date) \
                                .values('product_variant__product__product_brand__brand_name') \
                                .annotate(total_quantity=Sum('quantity')) \
                                .order_by('-total_quantity')[:5]                            
    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'dates': dates,
        'total_revenue':total_revenue,
        'orders_data': orders_data,
        'revenue_data': revenue_data,
        'order_status_data': order_status_data,
        'top_products': top_products,
        'top_variants': top_variants,
        'top_brands': top_brands,
        'time_range': time_range,
    }
    
    return render(request, 'AdminSide/admin-dashboard.html', context)


def admin_login(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)       
        if user is not None:    
            if user.is_admin:
             
                login(request, user)
                
                return redirect('admin_page')            
            else:
                messages.error(request, 'You are not authorized to access this page.')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'AdminSide/admin_login.html')



@user_passes_test(is_admin)
def users_list(request):
     users = User.objects.filter(is_admin=False) 
     return render(request, 'AdminSide/user_list.html', {'users': users})
    
   
    
@user_passes_test(is_admin)    
def documentaion(request):
    return render(request,'AdminSide/documentation.html')


@never_cache
@user_passes_test(is_admin)
def Block_user(request):
    blocking_mail = request.POST.get('email')
    user = get_object_or_404(User, email=blocking_mail)

    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True

    user.save()
    return redirect('users_list')

@user_passes_test(is_admin)
def admin_order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'AdminSide/admin_order_list.html', {'orders': orders})

@user_passes_test(lambda user: user.is_superuser)
def change_order_status(request, order_id):
    if request.method == 'POST':
       
        order = get_object_or_404(Order, id=order_id)
        
        status = request.POST.get('status')
        if status in ['Pending', 'Delivered', 'Accepted', 'Rejected']:
            order.status = status
            order.save()
        return redirect('admin_order_list')

@user_passes_test(is_admin)
def return_list(request):
    return_item = Return.objects.exclude(status='complete').order_by('-return_date')
    return render(request, "AdminSide/return_list.html", {'return_item': return_item})


 

@require_POST
@user_passes_test(is_admin)
def update_return_status(request):
    try:
        data = json.loads(request.body)
        return_id = data.get('return_id')
        new_status = data.get('status')
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    if not return_id or not new_status:
        return JsonResponse({'status': 'error', 'message': 'Missing return_id or status'}, status=400)

    with transaction.atomic():
        try:
            return_item = Return.objects.select_for_update().get(id=return_id)

            if return_item.status != 'Pending':
                return JsonResponse({'status': 'error', 'message': 'This return has already been processed'}, status=400)

            return_item.status = 'returned' if new_status == 'complete' else new_status
            return_item.save()

            if new_status == 'complete':
                order_items = OrderItem.objects.filter(order=return_item.order, product_variant__in=return_item.order.items.values_list('product_variant', flat=True))

                if not order_items.exists():
                    return JsonResponse({'status': 'error', 'message': 'Associated order items not found'}, status=404)

                total_refund_amount = 0
                
                for order_item in order_items:
                    refund_amount = order_item.paid_price-order_item.shipping
                    total_refund_amount += refund_amount
                    
                    product_variant = order_item.product_variant
                    product_variant.variant_stock += order_item.quantity
                    product_variant.save()

                wallet, _ = Wallet.objects.get_or_create(user=return_item.user)
                wallet.balance += total_refund_amount
                wallet.save()

                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=total_refund_amount,
                    description=f'Refund for return {return_item.id}',
                    transaction_type='Credit'
                )

                Payment.objects.filter(order=return_item.order).update(status='refund')
                Order.objects.filter(id=return_item.order.id).update(status='Returned')

                messages.success(request, 'Return approved, refund processed, and stock updated')
                return JsonResponse({'status': 'success', 'message': 'Return approved, refund processed, and stock updated'})

            elif new_status == 'rejected':
                messages.info(request, 'Return rejected')
                return JsonResponse({'status': 'success', 'message': 'Return rejected'})

            else:
                messages.info(request, 'Return status updated')
                return JsonResponse({'status': 'success', 'message': 'Return status updated'})

        except Return.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Return not found'}, status=404)
        except OrderItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Associated order item not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'}, status=500)


from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum, F
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


@user_passes_test(is_admin)
def sales_report(request):
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')
    report_type = request.GET.get('report_type', 'daily')

    orders = Order.objects.filter(status="Delivered")

    start_date = None
    end_date = None

    # Date range calculation based on report type
    if start_date_str and end_date_str:
        try:
            if report_type == 'daily':
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            elif report_type == 'monthly':
                start_date = datetime.strptime(start_date_str, '%Y-%m').date().replace(day=1)
                end_date = (datetime.strptime(end_date_str, '%Y-%m').date().replace(day=1) +
                            relativedelta(months=1) - timedelta(days=1))
            elif report_type == 'yearly':
                start_date = datetime.strptime(start_date_str, '%Y').date().replace(month=1, day=1)
                end_date = datetime.strptime(end_date_str, '%Y').date().replace(month=12, day=31)

            if start_date and end_date:
                # Ensure end_date includes the whole day
                end_date = end_date + timedelta(days=1)
                orders = orders.filter(created_at__range=[start_date, end_date])
        except ValueError:
            start_date_str = ''
            end_date_str = ''

    # Apply aggregation based on the report type
    if report_type == 'monthly':
        orders = orders.annotate(report_date=TruncMonth('created_at')).order_by('-report_date', '-created_at')
    elif report_type == 'yearly':
        orders = orders.annotate(report_date=TruncYear('created_at')).order_by('-report_date', '-created_at')
    else:  # daily
        orders = orders.annotate(report_date=TruncDay('created_at')).order_by('-report_date', '-created_at')

    # Calculate discount for each order
    orders = orders.annotate(
        discount=F('total_price') - F('final_price'),
        coupon_discount=F('offer_price')
    )

    # Aggregate total values
    total_stats = orders.aggregate(
        total_order_amount=Sum('final_price'),
        total_discount=Sum('discount'),
        total_coupon_discount=Sum('coupon_discount')
    )

    # Pagination
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except (EmptyPage, PageNotAnInteger):
        page_obj = paginator.page(1)

    # Format start and end date for display
    start_date_str = start_date.strftime('%Y-%m-%d') if start_date else ''
    end_date_str = (end_date - timedelta(days=1)).strftime('%Y-%m-%d') if end_date else ''

    context = {
        'page_obj': page_obj,
        'orders': page_obj,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'report_type': report_type,
        'total_order_amount': total_stats['total_order_amount'] or 0,
        'total_discount': total_stats['total_discount'] or 0,
        'total_coupon_discount': total_stats['total_coupon_discount'] or 0,
    }

    return render(request, 'AdminSide/sales_report.html', context)
