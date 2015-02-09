from django.conf.urls import patterns, include, url
from simpleipam import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'simpleipam.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    #############################################
    ## HTML page URLs
    url(r'^pools$', views.index, name='pools'),
    url(r'^pool/(?P<name>.*)$', views.pool, name='p_pool'),
    url(r'^admin/', include(admin.site.urls)),
    #############################################
    ## REST API URLs
    url(r'^api/pool$', views.PoolView.as_view(), name='pool'),
    url(r'^api/ip/allocate/(?P<pool>.*)/(?P<number>\d+)$', views.IpAllocateView.as_view(), name='ip_allocate'),
    #url(r'^ip/extrainfo/(?P<address>.*)$', views.IpAddressExtraInfoView.as_view(), name='extrainfo'),
    url(r'^api/ip/revoke$', views.IpRevokeView.as_view(), name='ip_revoke'),
)

urlpatterns += patterns('',
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)
