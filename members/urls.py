from django.urls import path
from .import views

urlpatterns = [
    path('login_user',views.login_user,name="login"),
    path('register_user',views.register_user,name="register"),
    path('logout_user',views.logout_user,name="logout"),
    path('my_account', views.my_account, name="my-account"),
    path('reset_password', views.reset_password, name="reset-password"),
    path('enter_username', views.enter_username, name="enter-username"),
    path('get_phone', views.get_phone, name="get-phone"),
    path('send_verification_code', views.send_verification_code, name="send-code"),
    # path('code_verification', views.code_verification, name="code-verification"),
    path('enter_verification_code', views.enter_verification_code, name="enter-code"),
    path('register_profile', views.register_profile, name="register-profile"),
    path('update_profile', views.update_profile, name="update-profile"),
    
]
