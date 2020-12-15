from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from Address.views import *


urlpatterns = [
    url(r'^$', AddressView.as_view(), name= 'address'),
]
