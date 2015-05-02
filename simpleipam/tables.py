'''
Created on Feb 22, 2015

@author: Autumn
'''

import django_tables2 as tables
from simpleipam.models import IpAddress, IpPool
from django_tables2.utils import A

class IpAddressTable(tables.Table):
    address = tables.LinkColumn('edit_address',accessor='ip_address', 
                                args=[A('ip_address')])
    used = tables.BooleanColumn()
    state = tables.Column()
    comments = tables.Column()
    pool = tables.Column(accessor='pool.name')
    vlan = tables.Column(accessor='pool.vlan')
    class Meta:
        model = IpAddress
        attrs = {"class": "paleblue"}
        fields = ('pool', 'address', 'vlan', 'used', 'state', 'comments')

class IpPoolTable(tables.Table):
    name = tables.LinkColumn("p_pool", args=[A('name')])
    ip_ranges = tables.Column()
    vlan = tables.Column()
    is_active = tables.BooleanColumn()
    comments = tables.Column()
    subnet = tables.Column(accessor="subnet_str", order_by=('subnet', 'maskbit'))
    
    class Meta:
        model = IpPool
        attrs = {"class": "paleblue"}
        fields = ('name', 'subnet', 'ip_ranges', 'vlan', 'is_active', 'comments')
        
        