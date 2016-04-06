'''
Created on Apr 6, 2016

@author: Autumn
'''

def ip_to_int(address):
    sets = address.ip_address.split('.')
    return int(sets[0])*256**3 + int(sets[1])*256**2 + int(sets[2])*256 + int(sets[3])

def sort_ips(ips):
    return sorted(ips, key=ip_to_int)


    
    
