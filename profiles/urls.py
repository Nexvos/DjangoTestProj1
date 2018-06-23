from django.urls import path

from . import views

app_name = 'profiles'
urlpatterns = [
    path('public/<username>/', views.profile_public, name='profile-public'),
    path('', views.profile_list_view, name='profile-list'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/add-funds/', views.profile_add_funds, name='profile-add-funds'),
]