from django.contrib import admin
from django.urls import path
from .views import user_login, user_logout, user_signup, index, home, about, faq, contact, recommendation

urlpatterns = [
        # Authentication URLs
    path("", user_login, name="login"),
    path("signup/", user_signup, name="signup"),
    path("logout/", user_logout, name="logout"),
    path("index/", index, name="index"),
    path("home/", home, name="home"),
    path("about/", about, name="about"),
    path("faq/", faq, name="faq"),
    path("contact/", contact, name="contact"),
    path("recommendation/", recommendation, name="recommendation"),
    
]

