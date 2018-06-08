from django.urls import path

from . import views

app_name = 'profiles'
urlpatterns = [
    path('<username>/', views.profile_view, name='profile'),
    path('', views.profile_list_view, name='profile-list'),

]