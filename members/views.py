from django.shortcuts import render,redirect, HttpResponseRedirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import RegisterUserForm,UserProfileForm
from django.shortcuts import get_object_or_404
from django.utils import timezone
import random
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from .models import PasswordResetToken, Profile
from utils.sms_utils import send_sms, verify_verification_code
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# def code_verification(request):

#     return render(request, 'authenticate/enter_verification.html')

def enter_username(request):

    return render(request, 'authenticate/enter_username.html')

def get_phone(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        print(username)
        # Get the user associated with the entered username
        user = User.objects.get(username=username)
        print(user.pk)
        # Get the profile of the user
        profile = Profile.objects.get(customer_id=user.pk)
        print(profile)
        # retreive the  phone number in the session
        phone_number = str(profile.mobile)
        print(phone_number)
        # Store the phone number in the session
        request.session['phone_number'] = phone_number
        request.session['username'] = username
        return render(request, 'authenticate/get_phone.html',{'username':username, 'phone_number':phone_number})
    
def send_verification_code(request):
    if request.method == 'POST':
        # Retrieve the username from the session
        phone_number = request.session['phone_number']
        print(phone_number)
        verification_code = generate_verification_code()
        phone = phone_number.lstrip('+254')
        print(phone)
        message = f"Your verification code is: {verification_code}"
        response = send_sms(phone, message)  # Pass both phone_number and message
        request.session['verification_code'] = verification_code
        # Process the response
        try:
            response_data = json.loads(response)
            print(response)
            response_code = response_data["responses"][0]["response-code"]
            # print(response_code)
            if response_code == 200:
                # If the response code indicates success
                # return JsonResponse({'status': 'success', 'message': 'Verification code sent successfully'})
                 # Redirect the user to the verification page with a success message
                return redirect('enter-code')
            else:
                # If the response code indicates an error
                return JsonResponse({'status': 'error', 'message': 'Failed to send verification code. Please try again later.'})
        except json.JSONDecodeError:
            # If there was an error decoding the JSON response
            return JsonResponse({'status': 'error', 'message': 'Failed to decode response. Please try again later.'})
        except KeyError:
            # If the response JSON structure is unexpected
            return JsonResponse({'status': 'error', 'message': 'Unexpected response structure. Please try again later.'})
    else:
        # Render the form to input phone number
        return render(request, 'authenticate/generate_code.html')
    
def reset_password(request):
    if request.method == 'POST':
        username = request.session['username']
        print(username)
        # Retrieve the user object associated with the username
        user = User.objects.get(username=username)
        print(user)
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            print('hello')
            form.save()
            update_session_auth_hash(request, form.user)# Keep the user logged in
            print(form.user)
            return redirect('index')
        else:
            print(form.errors)
            # If the form is invalid, render the form again with appropriate error messages
            return render(request, 'authenticate/reset_password.html', {'form': form})
    else:
        form = SetPasswordForm(request.user)
    return render(request, 'authenticate/reset_password.html', {'form': form})

def generate_verification_code():
    return str(random.randint(10000, 99999))

def enter_verification_code(request):
    if request.method == 'POST':
        entered_verification_code = request.POST.get('verification_code')
        print(entered_verification_code)
        generated_verification_code = request.session.get('verification_code')
        print(generated_verification_code)

        if generated_verification_code is not None and entered_verification_code == generated_verification_code:
            # if entered_verification_code == generated_verification_code:
            # Verification successful, redirect to password reset page
            return redirect('reset-password')
        else:
            # Verification failed, display error message
            messages.error(request, "Invalid verification code. Please try again.")
            return redirect('enter-code')  # Redirect back to verification code entry page
    else:
        # Handle GET request if needed
        return render(request, 'authenticate/enter_verification.html')
    
def register_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            mobile = form.cleaned_data['mobile']
            address = form.cleaned_data['address']
            block = form.cleaned_data['block']
            room = form.cleaned_data['room']
            profile_image = form.cleaned_data['profile_image']
            Profile.objects.create(
                customer=request.user,
                profile_image = profile_image,
                mobile=mobile,
                address=address,
                block=block,
                room=room, 
            )
            return redirect("index")
    else:
        form = UserProfileForm()
    return render(request, 'authenticate/register_profile.html', {'form': form})

@login_required
def update_profile(request):
    user = request.user
    profile = Profile.objects.get(customer=request.user)
    if request.method == 'POST':    
        form = UserProfileForm(request.POST or None, request.FILES or None, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("account")  # Redirect to user profile detail page
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'authenticate/update_profile.html', {'form': form})
    
def my_account(request):
    user_profile = request.user
    profile = Profile.objects.get(customer = request.user)
    # try:
    #     user_profile = user.userprofile
    # except UserProfile.DoesNotExist:
    #     user_profile = UserProfile.objects.create(user=user)  # Create user profile if it doesn't exist
    
    return render(request, 'main/account.html', {'user_profile':user_profile,'profile':profile})

def logout_user(request):
    logout(request)
    messages.success(request,("You were logged out"))
    return redirect('index')

def register_user(request):
    if request.method =="POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            #after registered, log them in
            customer = authenticate(username=username,password=password)
            login(request,customer)
            messages.success(request,("Registration succesful"))
            return redirect('register-profile')
    else:
        form = RegisterUserForm()
    return render(request,"authenticate/register.html",{'form':form})

def login_user(request):
    if request.method =="POST":
        username = request.POST['username']
        password = request.POST['password']
        customer = authenticate(request,username=username,password=password)
        if customer is not None:
            login(request,customer)
            return redirect('index')
        else:
            messages.success(request,("There was an error,Try again!"))
            return redirect('login')
    else:
        return render(request,"authenticate/login.html")

