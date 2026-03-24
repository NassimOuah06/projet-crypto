from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path("login/", views.login_user, name="login"),  # Connexion pour Admin, Med, Pat
    path("logout/", views.logout_user, name="logout"),  # Déconnexion pour Admin, Med, Pat
]
