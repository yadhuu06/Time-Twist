from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from order_management.models import Return
from UserAccounts.models import User
from django.shortcuts import get_object_or_404
from order_management.models import Order, Payment, OrderItem 
from user_pannel.models import UserAddress
from cart.models import Wallet, WalletTransaction
from products.models import Products,ProductVariant
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST


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
    return_item = Return.objects.all().order_by('-return_date')
    return render(request, "AdminSide/return_list.html", {'return_item': return_item})

@user_passes_test(is_admin)
@require_POST
def update_return_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        return_id = data.get('return_id')
        new_status = data.get('status')
        
        try:
            return_item = Return.objects.get(id=return_id)
            return_item.status = new_status
            return_item.save()

            if new_status == 'complete':
                # Calculate refund amount
                order_item = return_item.order_item
                refund_amount = order_item.total_price
                
                # Get user's wallet
                wallet = Wallet.objects.get(user=return_item.user)
                wallet.balance += refund_amount
                wallet.save()

                # Record transaction
                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=refund_amount,
                    description=f'Refund for return {return_item.id}',
                    transaction_type='credit'
                )

            return JsonResponse({'status': 'success'})
        except Return.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Return not found'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


from datetime import datetime, timedelta, date
from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models.functions import TruncMonth, TruncYear
from dateutil.relativedelta import relativedelta

@user_passes_test(is_admin)
def sales_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    report_type = request.GET.get('report_type', 'daily')
    
    # Filter orders where status is "Delivered"
    orders = Order.objects.filter(status="Delivered")
    
    if start_date and end_date:
        try:
            if report_type == 'daily':
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            elif report_type == 'monthly':
                start_date = datetime.strptime(start_date, '%Y-%m').date().replace(day=1)
                end_date = (datetime.strptime(end_date, '%Y-%m') + relativedelta(months=1) - timedelta(days=1)).date()
            elif report_type == 'yearly':
                start_date = datetime.strptime(start_date, '%Y').date().replace(month=1, day=1)
                end_date = datetime.strptime(end_date, '%Y').date().replace(month=12, day=31)
            
            # Add one day to end_date to include the end date in the results
            end_date = end_date + timedelta(days=1)
            orders = orders.filter(created_at__range=[start_date, end_date])
        except ValueError:
            # If date parsing fails, reset the filter
            start_date = None
            end_date = None
    
    if report_type == 'monthly':
        orders = orders.annotate(report_date=TruncMonth('created_at')).order_by('-report_date', '-created_at')
    elif report_type == 'yearly':
        orders = orders.annotate(report_date=TruncYear('created_at')).order_by('-report_date', '-created_at')
    else:  
        orders = orders.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Convert back to string for form display
    start_date_str = start_date.strftime('%Y-%m-%d') if isinstance(start_date, date) else ''
    end_date_str = end_date.strftime('%Y-%m-%d') if isinstance(end_date, date) else ''
    
    return render(request, 'AdminSide/sales_report.html', {
        'page_obj': page_obj,
        'orders': page_obj,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'report_type': report_type,
    })
