from django.urls import path
from . import views

app_name='accounts'

urlpatterns = [
    path('login/', views.admin_dashboard, name='login'),
    path('logout/', views.logout_view, name='logout'),
    #path("sign_up/", views.customer_signup, name="customer_signup"),
    #path("customer_login/", views.customer_login, name="customer_login"),
    #path("customer_logout/", views.customer_logout, name="customer_logout"),
    
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
]