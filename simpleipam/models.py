from django.db import models

# Create your models here.

class IpPool(models.Model):
    name = models.CharField(max_length=64, null=False, unique=True, db_index=True)
    subnet = models.IPAddressField()
    maskbit = models.IntegerField()
    ip_ranges = models.TextField(max_length=1024, null=False)
    vlan = models.CharField(max_length=32, null=True)
    comments = models.TextField(default="")
    is_active = models.BooleanField(default=True)
    createtime = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return "%s %s/%d : %s" % (self.name, self.subnet, self.maskbit, self.ip_ranges)


class IpAddress(models.Model):
    pool = models.ForeignKey(IpPool)
    ip_address = models.IPAddressField(unique=True, db_index=True)
    used = models.BooleanField(default=False)
    createtime = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(default="")
    #-1 : unknown, 0 - live, 1 - dead
    status = models.IntegerField(default=-1)
    
    def __unicode__(self):
        return "%s : %s [%r]" % (self.pool.name, self.ip_address, self.used)
    

'''
class IpAddressExtrInfo(models.Model):
    address = models.ForeignKey(IpAddress)
    comments = models.TextField(default="")
    
    def __unicode__(self):
        return "%s : %s" % (self.address.ip_address, self.comments[:32])
''' 
