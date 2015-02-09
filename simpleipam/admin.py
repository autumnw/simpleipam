'''
Created on 11/04/2014

@author: Autumn
'''
from django.contrib import admin
from simpleipam.models import IpPool, IpAddress


# Register your models here.
admin.site.register(IpPool)
admin.site.register(IpAddress)
