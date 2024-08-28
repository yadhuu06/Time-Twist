from django import forms
from .models import Coupon

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['coupon_name', 'minimum_amount', 'discount', 'maximum_amount', 'expiry_date', 'coupon_code', 'status']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_discount(self):
        discount = self.cleaned_data.get('discount')
        if discount < 1 or discount > 99:
            raise forms.ValidationError('Discount must be between 1 and 99.')
        return discount
