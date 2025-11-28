from django.urls import path
from . import views   # import functions from views.py

urlpatterns = [
    path('', views.home, name='home'),   # when someone visits "/", call home view
    path("signup/", views.signup, name="signup"),
    path("checkout/", views.checkout, name="checkout"),
    path('success/', views.success, name='success'),
    path('signin/', views.signin, name='signin'),
    #path("signup/", views.signup, name="signup"),
    path("success/", lambda request: render(request, "success.html"), name="success"),
]
