from netaddr.ip import IPAddress, IPRange, IPNetwork
from rest_framework.views import APIView
from rest_framework.response import Response

import logging
from rest_framework import permissions
from simpleipam.models import IpPool, IpAddress
from simpleipam.serializers import IpAddressSerializer, IpPoolSerializer
from django.shortcuts import render
from django_tables2   import RequestConfig
from simpleipam.tables import IpAddressTable, IpPoolTable
from simpleipam.forms import IpAddressForm, IpPoolForm
from django.http.response import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

from django_tables2 import SingleTableView
from simpleipam import models
from simpleipam.filters import AddressFilter
from simpleipam.utils import sort_ips

logger = logging.getLogger('simpleipam.file')

@login_required(login_url='/login/')
def index(request):
	pools = IpPool.objects.all()

	table = IpPoolTable(pools)
	RequestConfig(request, paginate={"per_page": 20}).configure(table)
	return render(request, 'simpleipam/pagi_index.html', {'table': table})

def healthcheck(request):
	return HttpResponse("OK")

@login_required(login_url='/login/')
def pool(request, name):
	the_pool = IpPool.objects.filter(name=name).first()
	addresses = IpAddress.objects.filter(pool=the_pool)
	address = request.GET.get('address', None) 
	comments = request.GET.get('comments', None)
	if address:
		if address[-1] == '*':
			addresses = addresses.filter(ip_address__contains=address[:-1])
		else:
			addresses = addresses.filter(ip_address=address)
	if comments:
		addresses = addresses.filter(comments__icontains=comments)
		
	table = IpAddressTable(addresses.all())
	pool = the_pool.name
	RequestConfig(request, paginate={"per_page": 20}).configure(table)
	context = {'table': table, 'pool':pool}
	return render(request, 'simpleipam/pagi_addresses.html', context)

@permission_required('simpleipam.add_ippool', login_url='/login/')
def create_pool(request):
	if request.method == 'GET':
		data = {'path' : request.path}
		form = IpPoolForm(initial=data)
		return render(request, 'simpleipam/createpool.html', {'form':form})
	else:
		view = PoolView()
		request.DATA = request.POST
		view.post(request)
		return HttpResponseRedirect(reverse('pools'))

@permission_required('simpleipam.change_ipaddress', login_url='/login/')
def edit_address(request, address):
	if request.method == 'GET':
		the_address = IpAddress.objects.filter(ip_address=address).first()
		data = {"ip_address": the_address.ip_address,
				"used" : the_address.used,
				"comments" : the_address.comments,
				"path" : request.path,
				"pool" : the_address.pool}
		form = IpAddressForm(initial=data)
		context = {'form': form}
		return render(request, 'simpleipam/editaddress.html', context)
	else:
		ip = request.POST['ip_address']
		ip_address = IpAddress.objects.filter(ip_address=ip).first()
		ip_address.comments = request.POST['comments']
		used = True
		if not request.POST.has_key('used'):
			used = False
		ip_address.used = used
		ip_address.save()
		pool = ip_address.pool.name
		return HttpResponseRedirect(reverse('p_pool', kwargs={'name': pool}))
	
	
class PoolView(APIView):
	
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
	
	# '''
	def get(self, request, pool=None):
	
		# print "Start get in PoolView"
		
		pools = IpPool.objects
		if pool:
			pools = pools.filter(name=pool)
		pools = pools.all()
		if not pools:
			return Response(data="Pool does not exist", status=400)
		
		return Response([IpPoolSerializer(p).data for p in pools])
	# '''
	
	def __populate_ip_addresses__(self, pool):
		for r in pool.ip_ranges.split(','):
			tmp_list = r.split('~')
			start_ip = tmp_list[0].strip()
			end_ip = tmp_list[1].strip()
			the_range = IPRange(start_ip, end_ip)
			ip = the_range.first
			while(ip <= the_range.last):
				addr = IpAddress()
				addr.pool = pool
				addr.ip_address = IPAddress(ip)
				addr.save()
				ip += 1
			print "polupate ip ranges"
			
	def __check_ip_range_conflict__(self, exist_ranges, curr_range):
		if curr_range in exist_ranges:
				raise Exception("IP range : %s is already allocated." % curr_range)
		for exist_range in exist_ranges:
			(a, b) = exist_range.split('~')
			exist_start = IPAddress(a.strip()).value
			exist_end = IPAddress(b.strip()).value + 1
			
			(c, d) = curr_range.split('~')
			start = IPAddress(c.strip()).value
			end = IPAddress(d.strip()).value
			
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
			r = r.strip()
			self.__check_ip_range_conflict__(exist_ranges, r)
			
			(start, end) = r.split('~')
			print "start = %s, end = %s" % (start, end)
			start_ip = IPAddress(start.strip()).value
			end_ip = IPAddress(end.strip()).value
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
		
		print "subnet=%r, maskbit=%d" % (subnet, maskbit)
		
		
		if not data.has_key('ip_ranges'):
			return Response(data="ip_range is required, format: 192.168.1.19~192.168.1.200, 192.168.1.220~192.168.1.254." , status=400)
			
		ranges = data['ip_ranges']
		
		pool = IpPool()
		pool.name = name
		pool.subnet = subnet
		pool.maskbit = maskbit
		pool.ip_ranges = ranges
		pool.vlan = data['vlan']
		
		if data.has_key('comments'):
			pool.comments = data['comments']
			
		if not pool.comments:
			pool.comments = ""
		try:
			self.__validate_ip_ranges__(pool)
		except Exception as e:
			print "exception : %s" % e
			return Response(data=e.message, status=400)
		
		try:
			pool.save()
			self.__populate_ip_addresses__(pool)
		except Exception as e:
			logger.exception(e)
			return Response(data=e.message, status=500)
		return Response(data=IpPoolSerializer(pool).data, status=200)
 
 
class PoolIpView(APIView):
	
	permission_classes = (permissions.IsAuthenticated,)
	
	def get(self, request, pool, used='all', comments=None):
		# print "Get in PoolIpView, pool : %s, used = %s" % (pool, used)
		ip_pool = IpPool.objects.filter(name=pool).first()
		# print "ip_pool = %r, comments=%r" % (ip_pool, comments)
		if not ip_pool:
			return Response(data='Pool %s does not exist' % pool, status=400)
		address_list = IpAddress.objects.filter(pool=ip_pool)
		# print "1. address_list = %r" % address_list.all()
		if comments and comments != 'None':
			print "Comments : %r" % comments
			address_list = address_list.filter(comments__contains=comments)
		# print "2. address_list = %r" % address_list.all()
		is_used = None 
		if used == 'used':
			is_used = True
		elif used == 'unused':
			is_used = False
		
		if is_used in [True, False]:
			address_list = address_list.filter(used=is_used)
		# print "3. address_list = %r, is_used = %r" % (address_list.all(), is_used)
		
		address_list = address_list.all()
		if not address_list:
			return Response(data='No ip address', status=400)
		
		return Response([IpAddressSerializer(a).data for a in address_list])
	
		   
class IpAllocateView(APIView):
	
	permission_classes = (permissions.IsAuthenticated,)
	
	def post(self, request):
		data = request.DATA
		pool = data['pool']
		number_of_ips = data['num_of_ips']
		comments = ""
		if data.has_key('comments') and data['comments']:
			comments = data['comments']
		
		ip_pool = IpPool.objects.filter(name=pool).first()
		unused_ips = IpAddress.objects.filter(pool=ip_pool, used=False).all()
		if unused_ips.count() == 0:
			return Response(data="The pool %s does not exist!" % pool, status=400)
		if unused_ips.count() < number_of_ips:
			return Response(data="No enough ips in this pool.", status=400)
		unused_ips = sort_ips(unused_ips)
		ip_list = []
		for the_ip in unused_ips[:number_of_ips]:
			ip_list.append(the_ip.ip_address)
			the_ip.used = True
			the_ip.comments = comments
			the_ip.save()
		return Response(ip_list)
	
	
class IpAddressView(APIView):
	
	permission_classes = (permissions.IsAuthenticated,)
	
	def put(self, request, address):
		
		try:
			ip = IPAddress(address)
		except Exception as e:
			logger.critical(e)
			return Response(data=e.message, status=400)
		
		data = request.DATA
		the_ip = IpAddress.objects.filter(ip_address=ip).first()
		if not the_ip:
			return Response(data="IP does not exist.", status=400)
		
		if data.has_key('comments'):
			the_ip.comments = data['comments']
		if data.has_key('used'):
			the_ip.used = data['used']
		if data.has_key('state'):
			the_ip.state = data['state']
		the_ip.save()
		return Response(IpAddressSerializer(the_ip).data)
		
	def get(self, request, address):
		try:
			ip = IPAddress(address)
		except Exception as e:
			logger.critical(e)
			return Response(data=e.message, status=400)
	
		the_ip = IpAddress.objects.filter(ip_address=ip).first()
		if not the_ip:
			return Response(data="IP does not exist.", status=400)
		return Response(IpAddressSerializer(the_ip).data)
	 

class IpRevokeView(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	
	def post(self, request):
		data = request.DATA
		ip_list = data['ip_addresses']
		for ip in ip_list:
			record = IpAddress.objects.get(ip_address=ip.strip())
			if record.used == False:
				continue
			record.used = False
			record.comments = ""
			record.save()
		return Response("Revoke ip addresses successfully.")
