from django import forms
from django.forms import ModelForm
from .models import Services,Products,Cart,All_Orders,Payments,Reviews, Team, Stores
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
class ServicesForm(ModelForm):
    class Meta:
        model = Services
        fields = ("service_image","service_name","description")

class ProductsForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ("product_name", "category", "product_price", "product_image", "description")

    CATEGORY_CHOICES = [
        ('Lunch', 'Lunch'),
        ('Breakfast', 'Breakfast'),
        ('Dinner', 'Dinner'),
    ]

    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    
class ReviewsForm(ModelForm):
    class Meta:
        model = Reviews
        fields = ("review_image","description")
        
class CartForm(ModelForm):
    class Meta:
        model = Cart
        fields = ("quantity",)

from django import forms
from .models import All_Orders
from members.models import Profile


from django.core.validators import RegexValidator



class OrdersForm(forms.ModelForm):
    mobile = forms.CharField(max_length=10, validators=[RegexValidator(r'^0\d{9}$', message="Mobile number must start with 0 and have 10 digits.")])

    class Meta:
        model = All_Orders
        fields = ("shipping_details","mobile") 
        

 




class PaymentsForm(ModelForm):
    class Meta:
        model = Payments
        fields = ("amount",)

#create a team form
class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = ("profile_name","profile_occupation","profile_image","quote")

#create office form
class StoresForm(ModelForm):
    class Meta:
        model = Stores
        fields = ("city","phone_number","email_address","physical_address","office_pic","basic_desc")
