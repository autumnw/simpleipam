'''
Created on Feb 23, 2015

@author: Autumn
'''
from django import forms
from django.forms import ModelForm
from simpleipam.models import IpAddress, IpPool

class IpAddressForm(ModelForm):
    used = forms.CheckboxInput()
    class Meta:
        model = IpAddress
        fields = ['ip_address', 'used', 'comments', 'pool']
        
class IpPoolForm(ModelForm):
    active = forms.CheckboxInput()
    ip_ranges = forms.IPAddressField()
    class Meta:
        model = IpPool
        fields = ['name', 'subnet', 'ip_ranges', 'vlan', 'is_active', 'comments']
        
    