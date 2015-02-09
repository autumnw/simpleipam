'''
Created on 09/19/2014

@author: Autumn
'''

#from django.contrib.auth.models import User, Group
from rest_framework import serializers
from simpleipam.models import IpPool, IpAddress

class IpPoolSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = IpPool
        fields = ('name', 'subnet', 'maskbit', 'vlan', 'ip_ranges', 'is_active', 'comments')


class IpAddressSerializer(serializers.ModelSerializer):
    
    pool = IpPoolSerializer(source="pool")
    class Meta:
        model = IpAddress
        fields = ('ip_address', 'used', 'pool')
    
'''    
class IpAddressExtrInfoSerializer(serializers.ModelSerializer):
    address = IpAddressSerializer(source="address")
    
    class Meta:
        model = IpAddressExtrInfo
        fields = ('address', 'comments')
'''        
        