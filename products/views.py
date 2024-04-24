from django.shortcuts import render,HttpResponse,HttpResponseRedirect,redirect
from django.contrib.auth.models import User
from .models import Services,Products,Cart,All_Orders,OrderItems,Payments,Reviews,Team,Stores
from .forms import ServicesForm,ProductsForm,OrdersForm,CartForm,ReviewsForm,TeamForm,StoresForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django_daraja.mpesa.core import MpesaClient
from phonenumber_field.phonenumber import PhoneNumber
from itertools import chain
from decimal import Decimal
from  django.db.models import Q 










def account(request):

    return render(request,"main/account.html")

def menu(request):
    products = Products.objects.all()
    lunch_products = Products.objects.filter(category='Lunch')
    break_products = Products.objects.filter(category='Breakfast')
    dinner_products = Products.objects.filter(category='Dinner')
    return render(request, "main/menu.html",{'products':products, 'lunch_products':lunch_products,'break_products':break_products, 'dinner_products':dinner_products})    

def send_message(request):
    if request.method=="POST":
        return render(request,"main/send_message.html")
    else:
        return render(request,"main/send_message.html")
def search_products(request):
    if request.method == "POST":
        searched = request.POST.get('searched', '')
        products = Products.objects.filter(
            Q(product_name__iexact=searched) | Q(product_name__icontains=searched)
        )
        print(products)

        if products:
            return render(request, 'main/search_products.html',
                          {'searched': searched, 'products': products})
        else:
            message = f"No products found for '{searched}'."
            return render(request, 'main/search_products.html',
                          {'searched': searched, 'message': message})
    else:
        return render(request, 'main/search_products.html', {})

    
def review_order(request,order_id):
    order = OrderItems.objects.get(pk=order_id)
    if request.method =="POST":
        form = ReviewsForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():
            description = form.cleaned_data['description']
            review_image = form.cleaned_data['review_image']
            #create the order
            Reviews.objects.create(
                customer = request.user,
                review_product = order.product,
                review_image = review_image,
                description = description,
                order = order,
            )
            order.reviewed_status = True
            order.save()
            messages.success(request,("Order reviewed successfully"))
        # else:
        #     messages.success(request,("Form is invalid"))
            return redirect('delivered')
    else:
        form = ReviewsForm()
    return render(request,"main/reviewside.html",{'form':form})
def update_delivered(request, order_id):
    order = OrderItems.objects.get(pk =order_id)
    order.parcel_collected_status = True
    order.parcel_arrived_status = True
    order.save()
    return redirect('review-orders')
def completed(request):
    order_items = OrderItems.objects.filter(
        customer=request.user,
        reviewed_status=True,
    )

    reviews = []

    for item in order_items:
        review = Reviews.objects.get(order_id=item.id)
        reviews.append(review)

    return render(request, 'main/completed.html', {'order_items': order_items, 'reviews': reviews})
def review_orders(request):
    order_items = OrderItems.objects.filter(
        customer = request.user,
        parcel_collected_status = True,
        parcel_arrived_status = True,
        reviewed_status = False,
    )
    return render(request,"main/review_orders.html",{'order_items':order_items})

@login_required
def delivered(request):
    order_item = OrderItems.objects.filter(
        customer = request.user,
        delivery_status = True,
        shipping_status = "Delivered Successfully",
        reviewed_status = False,
        parcel_collected_status = False,
    )
    return render(request, 'main/delivered.html',{'order_item':order_item})
def in_transit(request):
    order_item = OrderItems.objects.filter(
        customer=request.user, 
        payment_status = "Payment Succesful",
        shipping_status = "Packed,Ready for Delivery",
        delivery_status = False,
    )
    return render(request, 'main/in_transit.html',{'in_transit':in_transit,'order_item':order_item})

def pending_payment(request):
    order_item = OrderItems.objects.filter(
         customer = request.user,
         payment_status = "Pending Confirmation"
    )
    return render(request, 'main/pending_payment.html',{'order_item':order_item})


def payment(request):
    payment = Payments.objects.all().last()
    #latest('order_no')
    context ={'payment':payment}
    print(payment)
    return render(request,"main/payment.html",context)

def payments(request):
    payment = Payments.objects.all().last()
    cl = MpesaClient()
    token = cl.access_token()
    print(token)
    # Use a Safaricom phone number that you have access to, for you to be able to view the prompt.
    number = payment.mobile
    pho_number = str(number)
    amount = int(payment.amount)
    phone_number = "0" + pho_number[4:]
   
    
    account_reference = 'reference'
    transaction_desc = 'Description'
    callback_url = 'https://api.darajambili.com/express-payment'
    response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
    
    if response.status_code == 200:
        try:
            # Try to parse the JSON content from the response
            json_data = response.json()
            
            # Check if the response indicates success
            if isinstance(json_data, dict) and json_data.get('ResponseCode') == '0':
                # Redirect to the "my-orders" template upon success
                return redirect('my-orders')  # Replace 'my-orders' with the actual URL or view name for your "my-orders" template
            else:
                # Handle the case when the JSON response is not successful
                return HttpResponse(json_data)
        except ValueError:
            # Handle the case when the response content is not valid JSON
            return HttpResponse("Error: Unable to parse JSON response.")
    else:
        # Handle the case when the response status code is not 200
        return HttpResponse(f"Error: Unexpected status code - {response.status_code}")




    



# def  payments(request):
#     cl = MpesaClient()
#     phone_number = '0791508494'
#     amount = 1
#     account_reference = 'reference'
#     transaction_desc = 'Description'
#     callback_url = 'https://api.darajambili.com/express-payment'
#     response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
#     return HttpResponse(response)
#When  calculating the shipping  feee of  the customer 
def calculate_shipping_fee(total_amount):
    if total_amount == 0:
        return 0
    elif total_amount <= 100:
        return 20
    elif total_amount <= 200:
        return 35
    else:
        return 50


@login_required
def my_orders(request):
    order_items = OrderItems.objects.filter(
        customer=request.user,
        payment_status = "Pending Confirmation",
    )
    return render(request,"main/all_orders.html",{'order_items':order_items})
@login_required
def place_order(request,cart_id):
    cart = Cart.objects.get(pk=cart_id)
    #print(cart)
    if request.method =="POST":
        form = OrdersForm(request.POST)
        if form.is_valid():
            shipping_details = form.cleaned_data['shipping_details']
            mobile = form.cleaned_data['mobile']
            #print(mobile)
            #check
            product = cart.product
            # if product.product_stock >= cart.quantity:
            #     product.product_stock -= cart.quantity
            product.save()
            #create the order
            order = All_Orders.objects.create(
                customer = request.user,
                shipping_details = shipping_details,
                mobile = mobile,
                total = cart.total,
            )
            #add items from the cart to the order
            OrderItems.objects.create(
                order = order,
                product = cart.product,
                quantity = cart.quantity,
                price = cart.price,  
                customer = request.user,
                total = cart.total,         
            )
            #make the payent
            Payments.objects.create(
                customer = request.user,
                mobile = order.mobile,
                order_no = order,
                amount = order.total,
            )
            #clear the cart
            cart.delete()
        else:
            messages.error(request,("Form is invalid"))
        return redirect('payment')
    else:
        form = OrdersForm()
    return render(request,"main/sidebar.html",{'cart':cart,'form':form})
@login_required
def place_order_from_cart(request):
    cart = Cart.objects.filter(user=request.user)
    total_cost = 0.00
    for item in cart:
        total_cost += float(item.total)

    # Calculate shipping fee
    shipping_fee = calculate_shipping_fee(total_cost)

    if request.method == "POST":
        form = OrdersForm(request.POST)
        if form.is_valid():
            shipping_details = form.cleaned_data['shipping_details']
            mobile = form.cleaned_data['mobile']

            # Create the order
            order = All_Orders.objects.create(
                customer=request.user,
                shipping_details=shipping_details,
                mobile=mobile,
                total=Decimal(total_cost) + Decimal(shipping_fee),
            )

            # Add items from the cart to the order
            for item in cart:
                product = item.product
                # if product.product_stock >= item.quantity:
                #     product.product_stock -= item.quantity
                product.save()

                OrderItems.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.price,
                    customer=request.user,
                    total=item.price * item.quantity,
                )

            # Create payment entry
            Payments.objects.create(
                customer=request.user,
                mobile=order.mobile,
                order_no=order,
                amount=order.total,
            )

            # Clear the cart
            cart.delete()
            messages.success(request, "Your order has been placed successfully!")

            return redirect('payment')
        else:
            messages.error(request, "Form is invalid")

    else:
        form = OrdersForm()

    total_amount_to_pay = Decimal(total_cost) + Decimal(shipping_fee)

    return render(request, "main/place-order.html", {'cart': cart, 'form': form, 'total_cost': total_cost, 'shipping_fee': shipping_fee, 'total_amount_to_pay': total_amount_to_pay})

@login_required
def add_to_cart(request, product_id):
    try:
        product = Products.objects.get(id=product_id)
    except Products.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect('/')  # Or any other appropriate redirection

    quantity = 1
    Cart.objects.create(
        product=product,
        user=request.user,
        session_key=request.session.session_key,
        price=product.product_price,
        quantity=quantity,
        total=product.product_price * quantity,
    )
    messages.success(request, "Product added to cart successfully.")
    return redirect('/')


@login_required
def remove_from_cart(request, cart_id):
    try:
        item = Cart.objects.get(pk=cart_id)
    except Cart.DoesNotExist:
        messages.error(request, "Item not found in cart.")
        return redirect('cart')  # Or any other appropriate redirection

    if request.user == item.user:
        item.delete()
        messages.success(request, "Item removed from cart successfully.")
    else:
        messages.error(request, "You do not have permission to remove this item from the cart.")

    return redirect('cart')

@login_required
def update_cart_quantity(request, cart_id):
    try:
        cart = Cart.objects.get(pk=cart_id)
    except Cart.DoesNotExist:
        messages.error(request, "Item not found in cart.")
        return redirect('cart')  # Or any other appropriate redirection

    form = CartForm(request.POST, instance=cart)
    total = 0.00
    if form.is_valid():
        quantity = form.cleaned_data['quantity']
        cart.quantity = quantity
        cart.total = quantity * cart.price
        cart.save()
        messages.success(request, "Quantity updated successfully.")
        return redirect('cart')

    return render(request, 'main/quantity_update.html', {'cart': cart, 'form': form, 'total': total})


@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum([item.price * item.quantity for item in cart_items])
    
    # Calculate the total number of items in the cart
    items_count = sum(cart_item.quantity for cart_item in cart_items)

    # Check if the cart is empty
    is_cart_empty = not cart_items.exists()

    return render(request, 'main/cart.html', {'cart_items': cart_items, 'total': total, 'is_cart_empty': is_cart_empty, 'items_count': items_count})

def update_product(request,product_id):
    product = Products.objects.get(pk=product_id)
    form = ProductsForm(request.POST or None,request.FILES or None, instance=product)
    if form.is_valid():
        form.save()
        return redirect('list-products')
    return render(request, 'main/update_product.html',{'product':product, 'form':form})

def delete_product(request,product_id):
    product = Products.objects.get(pk=product_id)
    product.delete()
    return redirect('list-products')

def add_product(request):
    submitted = False
    if request.method=="POST":
        form = ProductsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/add_product? submitted = True")
    else:
        form = ProductsForm
        if "submitted" in request.GET:
            submitted = True
    return render(request,"main/add_product.html",{"submitted":submitted,"form":form})

def list_products(request):
    products = Products.objects.all()
    return render(request,"main/list_products.html",{'products':products})

def delete_team(request,team_id):
    team_member = Team.objects.get(pk=team_id)
    team_member.delete()
    return redirect('list-team')

def update_team(request,team_id):
    team = Team.objects.get(pk=team_id)
    form = TeamForm(request.POST or None, request.FILES or None, instance=team)
    #form = TeamForm(request.POST or None, request.FILES or None,instance=team)
    if form.is_valid():
        form.save()
        messages.success(request,("Team Member Updated Succesfully"))
        return redirect("list-team")
    return render(request,"main/update_team.html",{"team":team,"form":form})
    
def list_team(request):
    teams = Team.objects.all()
    return render(request, "main/list_team.html",{'teams':teams})

def add_team(request):
    submitted = False
    if request.method =="POST":
        form = TeamForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, ("Team member added succesfully"))
            return HttpResponseRedirect("/add_team? submitted = True")
    else:
        form = TeamForm
        if 'submitted' in request.GET:
            submitted = True
    return render(request, "main/add_team.html",{'submitted':submitted,'form':form})
def contact(request):
    stores = Stores.objects.all()
    return render(request,"main/contact.html",{'stores':stores})
def about(request):
    stores = Stores.objects.all()
    teams = Team.objects.all()
    services = Services.objects.all()
    return render(request,"main/about.html",{'services':services,'teams':teams,'stores':stores})

def index(request):
    reviews = Reviews.objects.all()
    products = Products.objects.all()
    services = Services.objects.all()
    return render(request,'main/index.html',{'services':services,"products":products,'reviews':reviews})
    
def admin_reviews(request):
    review_item = Reviews.objects.all()

    return render(request,"main/admin_review.html",{'review_item':review_item})

# import json
# import requests
# from django.shortcuts import redirect
# from django.contrib import messages
# from .models import Payments, All_Orders, OrderItems  # Import your models here

# def send_sms(phone_number, message):
#     url = "https://sms.textsms.co.ke/api/services/sendsms"
#     payload = {
#         "mobile": f'+254{phone_number}',
#         "response_type": "json",
#         "partnerID": '9785',
#         "shortcode": 'TextSMS',
#         'apikey': '7d0971b0a315bf420be231871cd1ef3c',
#         "message": message
#     }
#     headers = {
#         'Content-Type': 'application/json'
#     }
#     response = requests.post(url, headers=headers, data=json.dumps(payload))
#     return response.ok

# def admin_update_payment(request, record_id):
#     try:
#         # Retrieve the payment record
#         payment = Payments.objects.get(order_no_id=record_id)

#         # Update payment status
#         payment.payment_status = "Payment Successful"
#         payment.save()

#         # Retrieve necessary details for sending the confirmation message
#         phone_number = payment.mobile
#         username = payment.customer.username

#         print(username)

#         # Compose the payment confirmation message
#         message = f"Dear {username}, Payment has been received. Your order will be delivered shortly. Thank you for ordering at DEOX."

#         # Send the payment confirmation message
#         response = send_sms(phone_number, message)
#         print(response)

#         if response:
#             # If the message was sent successfully, redirect to the admin payments page
#             messages.success(request, "Payment confirmation message sent successfully.")
#         else:
#             # If sending the message fails, display an error message
#             messages.error(request, "Failed to send payment confirmation message.")

#     except Payments.DoesNotExist:
#         # Handle case where the payment record does not exist
#         messages.error(request, "Payment record does not exist.")

#     return redirect('admin-payments')


def admin_payments(request):
    payments = Payments.objects.all().order_by('-id')  
    orders = All_Orders.objects.all().order_by('-id')  
    return render(request,"main/admin_payment.html",{'payments':payments,'orders':orders})

def admin_completed(request):
    order_items = OrderItems.objects.filter(
        delivery_status = True,
        parcel_collected_status = True,
        parcel_arrived_status = True,
    )
    print(order_items)
    return render(request, 'main/admin_completed.html',{'order_items':order_items})

def admin_update_delivered(request, order_id):
    order = OrderItems.objects.get(pk =order_id)
    order.delivery_status = True
    order.shipping_status = "Delivered Successfully"
    order.save()
    return redirect('admin-delivered')

def admin_delivered(request):
    order_items = OrderItems.objects.filter(
        delivery_status = True,
        parcel_collected_status = False,
        parcel_arrived_status = False,
    )
    print(order_items)
    return render(request, 'main/admin_delivered.html',{'order_items':order_items})

def admin_paid_parcel(request):
    order_items = OrderItems.objects.filter(
        payment_status = "Payment Succesful",
        delivery_status = False,
    )
    return render(request, 'main/admin_paid_parcel.html',{'order_items':order_items})

def admin_pending_payment(request):
    order_items = OrderItems.objects.filter(
        payment_status = "Pending Confirmation"
    )
    return render(request, 'main/admin_pending_payment.html',{'order_items':order_items})
def admin_update_payment(request,record_id):
    order = Payments.objects.filter(order_no_id=record_id)
    all_order = order.values()
    print(all_order)
    k=all_order[0]
    print(k)
    my_id = k["order_no_id"]
    my_order = All_Orders.objects.filter(id=my_id)
    m_order = my_order.values()
    m = m_order[0]
    our_id = m["id"]
    print(our_id)
    our_order = OrderItems.objects.filter(order_id=my_id)
    for item in our_order:
        item.payment_status = "Payment Succesful"
        item.shipping_status = "Packed,Ready for Delivery"
        item.save()
    #print(my_order)
    return redirect('admin-payments')

def admin_orders(request):
    order_items = OrderItems.objects.all()
    print(order_items)    
    return render(request,"main/admin_orders.html",{'order_items':order_items})
def admin_users(request):
    users = User.objects.all()
    return render(request,"main/customers.html",{'users':users})
def administrator(request):
    #reviews = Reviews.objects.all()'reviews':reviews,
    products = Products.objects.all()
    services = Services.objects.all()
    payments = Payments.objects.all()
    cart = Cart.objects.all()
    orders = OrderItems.objects.all()
    all_orders = All_Orders.objects.all()
    return render(request,"main/administrator.html",{'products':products,'services':services,'payments':payments,'cart':cart,'orders':orders,'all_orders':all_orders})
