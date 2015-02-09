from netaddr.ip import IPAddress, IPRange, IPNetwork
#from netaddr.ip.sets import IPSet
#from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.

import logging
from rest_framework import permissions
from simpleipam.models import IpPool, IpAddress
from simpleipam.serializers import IpPoolSerializer
from django.template.context import RequestContext
from django.shortcuts import render
#, IpAddressSerializer
logger = logging.getLogger('simpleipam.file')

def index(request):
    
    pools = IpPool.objects.all()
    
    context = RequestContext(request, {
        'pools': pools
    })
    return render(request, 'simpleipam/index.html', context)

def pool(request, name):
    the_pool = IpPool.objects.filter(name=name).first()
    addresses =  IpAddress.objects.filter(pool=the_pool).all()
    '''
    total = len(addresses)
    page_size = 10
    page_num = total / page_size
    if (page_num * page_size) < total:
        page_num += 1
    
    context = RequestContext(request, {
        'addresses': addresses,
        'page_size': page_size,
        'pages' : range(1, page_num+1)
    })
    '''
    context = RequestContext(request, {
        'addresses': addresses
        })
    return render(request, 'simpleipam/addresses.html', context)

class PoolView(APIView):
    
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    
    #'''
    def get(self, request, name=None):
        pools = IpPool.objects.all()
        return Response([IpPoolSerializer(p).data for p in pools])
    #'''
    
    def __populate_ip_addresses__(self, pool):
        for r in pool.ip_ranges.split(','):
            tmp_list = r.split('~')
            start_ip = tmp_list[0]
            end_ip = tmp_list[1]
            the_range = IPRange(start_ip, end_ip)
            ip = the_range.first
            while(ip <= the_range.last):
                addr = IpAddress()
                addr.pool = pool
                addr.ip_address = IPAddress(ip)
                addr.save()
                ip += 1
            
    def __check_ip_range_conflict__(self, exist_ranges, curr_range):
        if curr_range in exist_ranges:
                raise Exception("IP range : %s is already allocated." % curr_range )
        for exist_range in exist_ranges:
            (a,b) = exist_range.split('~')
            exist_start = IPAddress(a).value
            exist_end = IPAddress(b).value + 1
            
            (c,d) = curr_range.split('~')
            start = IPAddress(c).value
            end = IPAddress(d).value
            
            if start in range(exist_start, exist_end) or \
                end in range(exist_start, exist_end):
                raise Exception("IP range : %s conflicts with existing range : %s" % (curr_range, exist_range))
        
    def __validate_ip_ranges__(self, pool):
        
        pools = IpPool.objects.all()
        exist_ranges = []
        for p in pools:
            exist_ranges.extend(p.ip_ranges.split(','))
        
        subnet = "%s/%d" % (pool.subnet, pool.maskbit)
        network = IPNetwork(subnet)
        low_ip = network.first
        up_ip = network.last + 1
        for r in pool.ip_ranges.split(','):
            
            self.__check_ip_range_conflict__(exist_ranges, r)
            
            (start, end) = r.split('~')
            start_ip = IPAddress(start).value
            end_ip = IPAddress(end).value
            if (start_ip not in range(low_ip, up_ip)) or \
                (end_ip not in range(low_ip, up_ip)):
                raise Exception("IP range: %s is not inside of subnet : %s" % (r, subnet))
        return True
    
    
    def post(self, request):
        data = request.DATA
        name = data['name']
        
        if IpPool.objects.filter(name=name).count() > 0:
            return Response(data="Pool %s already exists." % name, status=400)
        
        tmp_list = data['subnet'].split('/')
        if len(tmp_list) != 2:
            return Response(data="subnet is invalid.", status=400)
        subnet = tmp_list[0]
        maskbit = int(tmp_list[1])
        
        if not data.has_key('ip_ranges'):
            return Response(data="ip_range is required, format: 192.168.1.19~192.168.1.200, 192.168.1.220~192.168.1.254." ,status=400)
            
        ranges = data['ip_ranges']
        
        pool = IpPool()
        pool.name = name
        pool.subnet = subnet
        pool.maskbit = maskbit
        pool.ip_ranges = ranges
        pool.vlan = data['vlan']
        if data.has_key('comments'):
            pool.comments = data['comments']
        
        try:
            self.__validate_ip_ranges__(pool)
        except Exception as e:
            return Response(data=e.message, status=400)
        
        pool.save()
        try:
            self.__populate_ip_addresses__(pool)
        except Exception as e:
            logger.exception(e)
            return Response(data=e.message, status=500)
        return Response(status=200)
       
           
class IpAllocateView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, pool, number):
        ip_pool = IpPool.objects.filter(name=pool).first()
        unused_ips = IpAddress.objects.filter(pool=ip_pool, used=False).all()
        size = int(number)
        if unused_ips.count() == 0:
            return Response(data="The pool %s does not exist!" % pool, status=404)
        if unused_ips.count() < size:
            return Response(data="No enough ips in this pool.", status=400)
        ip_list = []
        for ip in unused_ips[:size]:
            ip_list.append(ip.ip_address)
            ip.used = True
            ip.save()
        return Response(ip_list)

'''
class IpAddressExtraInfoView(APIView):
    permission_classes = (permissions.IsAuthenticated,)  
      
    def post(self, request, address):
        data = request.DATA
        comments = data['comments']
        addr = IpAddress.objects.filter(ip_address=address).first()
        extra_info = IpAddressExtrInfo()
        extra_info.address = addr
        extra_info.comments = comments
        extra_info.save()
        return Response(data="Updated extra info for ip : %s successfully," % address, status=200)
'''    

class IpRevokeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        data = request.DATA
        ip_list = data['ip_addresses']
        for ip in ip_list:
            record = IpAddress.objects.get(ip_address=ip.strip())
            if record.used == False:
                continue
            record.used = False
            record.save()
        return Response("Revoke ip addresses successfully.")

