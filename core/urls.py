from django.urls import path
from . import views

urlpatterns = [
    # The homepage handles both GET (display) and POST (contact form submission)
    path('', views.home_view, name='home'), 
]