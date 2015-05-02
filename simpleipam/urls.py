from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from simpleipam import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
admin.autodiscover()

urlpatterns = patterns('',
    #############################################
    ## HTML page URLs
    url(r'^$', views.index, name='default'),
    url(r'^pools$', views.index, name='pools'),
    url(r'^pool/create$', views.create_pool, name='create_pool'),
    url(r'^pool/(?P<name>.*)$', views.pool, name='p_pool'),
    url(r'^ip/edit/(?P<address>.*)$', views.edit_address, name='edit_address'),
    #url(r'^pool/$', views.PoolDatatableView.as_view(), name='p_pool'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', auth_views.login),
    url(r'^logout/$', auth_views.logout),
    url(r'^healthcheck/$', views.healthcheck, name='healthcheck'),
    #############################################
    ## REST API URLs
    url(r'^api/pool/(?P<pool>.*)/(?P<used>.*)/(?P<comments>.*)$', views.PoolIpView.as_view(), name='pool'),
    url(r'^api/pool/(?P<pool>.*)/(?P<used>.*)$', views.PoolIpView.as_view(), name='pool'),
    url(r'^api/pool/(?P<pool>.*)$', views.PoolView.as_view(), name='pool'),
    url(r'^api/pool$', views.PoolView.as_view(), name='pool'),
    #url(r'^api/ip/allocate/(?P<pool>.*)/(?P<number>\d+)$', views.IpAllocateView.as_view(), name='ip_allocate'),
    url(r'^api/ip/revoke$', views.IpRevokeView.as_view(), name='ip_revoke'),
    url(r'^api/ip/allocate$', views.IpAllocateView.as_view(), name='ip_allocate'),
    url(r'^api/ip/(?P<address>.*)$', views.IpAddressView.as_view(), name='ip_address'),
    #url(r'^ip/extrainfo/(?P<address>.*)$', views.IpAddressExtraInfoView.as_view(), name='extrainfo'),
    
)

urlpatterns += patterns('',
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)
