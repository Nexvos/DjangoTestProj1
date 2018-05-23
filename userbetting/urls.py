from django.urls import path

from . import views

app_name = 'userBetting'
urlpatterns = [
    # ex: /betting/
    path('', views.index, name='index'),
    path('test/', views.testPage, name='test')
]