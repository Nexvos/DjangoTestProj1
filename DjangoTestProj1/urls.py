"""DjangoTestProj1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from DjangoTestProj1.views import home
from django.conf import settings
from django.conf.urls.static import static
from DjangoTestProj1.api import router




urlpatterns = [
    path('betting/', include('userbetting.urls')),
    path('profiles/', include('profiles.urls')),
    path('bettingadmin/', include('BettingAdmin.urls')),
    path('community/', include('community.urls')),
    path('admin/', admin.site.urls),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^api-test/', include(router.urls)),
    url(r'^$', home, name='home'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
