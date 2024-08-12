from django.shortcuts import render, redirect, get_object_or_404
from .models import UserAddress
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def add_address(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        house_name = request.POST.get('house_name')
        street_name = request.POST.get('street_name')
        pin_number = request.POST.get('pin_number')
        district = request.POST.get('district')
        state = request.POST.get('state')
        phone_number = request.POST.get('phone_number')

        # Check for duplicate address
        if UserAddress.objects.filter(user=request.user, house_name=house_name, street_name=street_name, pin_number=pin_number).exists():
            messages.error(request, 'This address already exists.')
            return redirect('user_profile')

        address = UserAddress(
            user=request.user,
            name=name,
            house_name=house_name,
            street_name=street_name,
            pin_number=pin_number,
            district=district,
            state=state,
            phone_number=phone_number,
            status=True,
        )
        address.save()
        messages.success(request, 'Address added successfully!')
        return redirect('user_profile')

    messages.error(request, "Failed to add address.")
    return redirect('user_profile')

@login_required
def edit_address(request, address_id):
    address = get_object_or_404(UserAddress, id=address_id, user=request.user)

    if request.method == 'POST':
        address.name = request.POST.get('name')
        address.house_name = request.POST.get('house_name')
        address.street_name = request.POST.get('street_name')
        address.pin_number = request.POST.get('pin_number')
        address.district = request.POST.get('district')
        address.state = request.POST.get('state')
        address.phone_number = request.POST.get('phone_number')


        if 'set_as_primary' in request.POST:
            UserAddress.objects.filter(user=request.user).update(status=False)
            address.status = True

        address.save()
        messages.success(request, 'Address updated successfully!')
        return redirect('user_profile')

    return render(request, 'edit_address.html', {'address': address})


@login_required
def delete_address(request, address_id):
    address = get_object_or_404(UserAddress, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully!')
        return redirect('user_profile')

    return render(request, 'UserSide/user-login/confirm_delete.html', {'address': address})