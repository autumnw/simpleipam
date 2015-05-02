'''
Created on Feb 26, 2015

@author: Autumn
'''
import django_filters
from simpleipam.models import IpAddress

class AddressFilter(django_filters.FilterSet):
    ip_address = django_filters.CharFilter(lookup_type='exact')

    class Meta:
        model = IpAddress
        fields = ['ip_address']