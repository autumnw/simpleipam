from django.db import models

# Create your models here.

class IpPool(models.Model):
    name = models.CharField(max_length=64, null=False, unique=True, db_index=True, verbose_name='pool name')
    subnet = models.IPAddressField()
    maskbit = models.IntegerField()
    ip_ranges = models.TextField(max_length=1024, null=False)
    vlan = models.CharField(max_length=32, null=True)
    comments = models.TextField(default="", null=True)
    is_active = models.BooleanField(default=True)
    createtime = models.DateTimeField(auto_now_add=True)
    
    @property
    def subnet_str(self):
        return u"%s/%s" % (self.subnet, self.maskbit)
    
    def __unicode__(self):
        return "%s %s/%d : %s" % (self.name, self.subnet, self.maskbit, self.ip_ranges)

    class Meta:
        permissions = (('view_ippool', 'Can view ippool'),
                       )
        

class IpAddress(models.Model):
    pool = models.ForeignKey(IpPool)
    ip_address = models.IPAddressField(unique=True, db_index=True)
    used = models.BooleanField(default=False)
    createtime = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(default="", null=True)
    ##########################################
    #-1 : unknown, 0 - live, 1 - dead
    state = models.IntegerField(default=-1)
    
    def __unicode__(self):
        return "%s : %s [%r]" % (self.pool.name, self.ip_address, self.used)
    
