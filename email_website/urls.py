"""email_website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from email_website import views

urlpatterns = [
    path('', views.subscribe, name='subscribe'),
    path('admin/', admin.site.urls),
    path('daily/<int:day>-<int:month>-<int:year>', views.show_article, name='show-article'),
    path('daily/unsubscribe/<uuid:uuid>', views.unsubscribe, name='unsubscribe'),
    path('confirm/<slug:slug>', views.confirm_email, name='confirm-email'),
    path('daily/latest/', views.show_latest, name='latest'),
    path('archive/', views.ArchiveView.as_view(), name='archive'),
    path('daily/stories/<slug:slug>', views.show_stories, name='stories'),
    path('thanks/', views.thanks_for_subscribing),
    path('privacy/', views.privacy, name='privacy'),
    path('responsibility/', views.responsibility, name='responsibility'),
    path('contacts/', views.contacts, name='contacts'),
    path('tinymce/', include('tinymce.urls'))
]
