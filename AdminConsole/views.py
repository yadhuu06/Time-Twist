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
from datetime import datetime, timedelta, date
from django.core.paginator import Paginator
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.db.models import Sum
import json

def is_admin(user):
    return  user.is_admin


@user_passes_test(is_admin)
@never_cache
def admin_page(request):
    return render(request,'AdminSide/admin-dashboard.html')
    



def admin_login(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)       
        if user is not None:    
            if user.is_admin:
             
                login(request, user)
                return render(request,'AdminSide/admin-dashboard.html')              
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
                    refund_amount = order_item.paid_price
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
                    transaction_type='credit'
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

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models.functions import TruncMonth, TruncYear, TruncDay

@user_passes_test(is_admin)
def sales_report(request):
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')
    report_type = request.GET.get('report_type', 'daily')

    orders = Order.objects.filter(status="Delivered")

    start_date = None
    end_date = None

    if start_date_str and end_date_str:
        try:
            if report_type == 'daily':
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            elif report_type == 'monthly':
                start_date = datetime.strptime(start_date_str, '%Y-%m').date().replace(day=1)
                end_date = (datetime.strptime(end_date_str, '%Y-%m').date() + relativedelta(months=1) - timedelta(days=1))
            elif report_type == 'yearly':
                start_date = datetime.strptime(start_date_str, '%Y').date().replace(month=1, day=1)
                end_date = datetime.strptime(end_date_str, '%Y').date().replace(month=12, day=31)

            if start_date and end_date:
             
                end_date = end_date + timedelta(days=1)
                orders = orders.filter(created_at__range=[start_date, end_date])
        except ValueError:
            start_date_str = ''
            end_date_str = ''

    if report_type == 'monthly':
        orders = orders.annotate(report_date=TruncMonth('created_at')).order_by('-report_date', '-created_at')
    elif report_type == 'yearly':
        orders = orders.annotate(report_date=TruncYear('created_at')).order_by('-report_date', '-created_at')
    else:  
        orders = orders.annotate(report_date=TruncDay('created_at')).order_by('-report_date', '-created_at')

    # Calculate discount for each order
    for order in orders:
        order.discount = order.total_price - order.final_price

    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except (EmptyPage, PageNotAnInteger):
        page_obj = paginator.page(1)

    start_date_str = start_date.strftime('%Y-%m-%d') if start_date else ''
    end_date_str = end_date.strftime('%Y-%m-%d') if end_date else ''


    context = {
        'page_obj': page_obj,
        'orders': page_obj,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'report_type': report_type,
        'total_order_amount': orders.aggregate(total_order_amount=Sum('final_price'))['total_order_amount'] or 0,
        'total_discount': orders.aggregate(total_discount=Sum('offer_price'))['total_discount'] or 0,
    }

    return render(request, 'AdminSide/sales_report.html', context)
