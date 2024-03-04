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
        searched = request.POST['searched']
        products = Products.objects.filter(product_name__contains = searched) 
        print(products)
        return render(request, 'main/search_products.html',
        {'searched':searched, 'products': products})
    else:
        return render(request, 'main/search_products.html',{})
    
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
    order_item = OrderItems.objects.filter(
        customer = request.user,
        reviewed_status = True,
    )
    for item in order_item:
        review = Reviews.objects.get(order_id = item.id)
    return render(request, 'main/completed.html',{'order_item':order_item,"review":review})

def review_orders(request):
    order_items = OrderItems.objects.filter(
        customer = request.user,
        parcel_collected_status = True,
        parcel_arrived_status = True,
        reviewed_status = False,
    )
    return render(request,"main/review_orders.html",{'order_items':order_items})

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
    print(payment)
    return render(request,"main/payment.html",{'payment':payment})

def payments(request):
    payment = Payments.objects.all().last()
    cl = MpesaClient()
    token = cl.access_token()
    print(token)
    # Use a Safaricom phone number that you have access to, for you to be able to view the prompt.
    number = payment.mobile
    pho_number = str(number)
    phone_number = "0" + pho_number[4:]
    amount = int(payment.amount)
    account_reference = 'reference'
    transaction_desc = 'Description'
    callback_url = 'https://api.darajambili.com/express-payment'
    response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
    return HttpResponse(response)
'''

def  payments(request):
    cl = MpesaClient()
    phone_number = '0791508494'
    amount = 1
    account_reference ='reference'
    transaction_desc = 'Description'
    callback_url = 'https://api.darajambili.com/express-payment'
    response = cl.stk_push(phone_number,amount,account_reference,transaction_desc,callback_url)
    return HttpResponse(response)
'''
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
            messages.success(request,("Form is invalid"))
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

            return redirect('payment')
        else:
            messages.success(request, "Form is invalid")

    else:
        form = OrdersForm()

    total_amount_to_pay = Decimal(total_cost) + Decimal(shipping_fee)

    return render(request, "main/place-order.html", {'cart': cart, 'form': form, 'total_cost': total_cost, 'shipping_fee': shipping_fee, 'total_amount_to_pay': total_amount_to_pay})

@login_required
def add_to_cart(request,product_id):
    product = Products.objects.get(id=product_id)
    quantity = 1
    Cart.objects.create(
        product = product,
        user = request.user,
        session_key = request.session.session_key,
        price=product.product_price,
        quantity = quantity,
        total = product.product_price * quantity,
        )
    return redirect('cart')

@login_required
def remove_from_cart(request,cart_id):
    item = Cart.objects.get(pk=cart_id)
    if request.user == item.user:
        item.delete()
    return redirect('cart')
@login_required
def update_cart_quantity(request,cart_id):
    cart = Cart.objects.get(pk=cart_id)
    form = CartForm(request.POST)
    total = 0.00
    if form.is_valid():
        quantity = form.cleaned_data['quantity']
        cart.quantity = quantity
        cart.total = quantity * cart.price
        cart.save()
        return redirect('cart')
    return render(request, 'main/quantity_update.html',{'cart':cart, 'form':form,'total':total})
@login_required
def cart(request):
    #Reviews.objects.all().delete()
    cart_items = Cart.objects.filter(
        user = request.user,
        #session_key = request.session.session_key
    )
    total = sum([item.price * item.quantity for item in cart_items])
    # Check if the cart is empty
    is_cart_empty = not cart_items.exists()

    return render(request,'main/cart.html',{'cart_items':cart_items,'total':total,'is_cart_empty':is_cart_empty})

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
def admin_payments(request):
    payments = Payments.objects.all()
    orders = All_Orders.objects.all()
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