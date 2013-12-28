#!/usr/bin/env python
import netinfo
from scapy.all import *
from scapy.layers.l2 import arping
import subprocess as sp
import platform


class TuxCut:
    def __init__(self, iface):
        self.iface = iface
        if platform.linux_distribution()[0] == 'Fedora':
            self.isfedora = True
        else:
            self.isfedora = False
        if not self.iface == '':
            print 'connected'
            self.myip = self.get_myip(self.iface)
            self.myhw = netinfo.get_hwaddr(self.iface)
            self.gwip = self.get_gwip()
            self.gwhw = self.get_gwhw()
            self.netmask = '24'
            self.enable_protection()
        else:
            print self.iface, 'No active connection detected'
            sys.exit()

        #self.protection_thread()

    def get_iface(self):
        ifaces_list = []
        ifaces_tupel = netinfo.list_active_devs()
        for iface in  ifaces_tupel:
            if not iface == 'lo':
                ifaces_list.append(iface)
        return ifaces_list[0]

    def get_myip(self,iface):
        return netinfo.get_ip(iface)

    def get_gwip(self):
        routes = netinfo.get_routes()
        for route in routes:
            if route['dest'] == '0.0.0.0' and route['dev'] == self.iface:
                return route['gateway']

    def get_gwhw(self):
        alive, dead = arping(self.gwip, verbose=False)
        try:
            return alive[0][1].hwsrc
        except:
            print sys.exc_info()[0], ' ', sys.exc_info()[1]

    def get_live_hosts(self):
        live_hosts = dict()
        live_hosts[self.myip] = self.myhw.lower()
        try:
            alive, dead = arping(self.gwip+'/'+self.netmask,  verbose=False)
            for i in range(0, len(alive)):
                live_hosts[alive[i][1].psrc] = alive[i][1].hwsrc
        except:
            print sys.exc_info()[0], '\n', sys.exc_info()[1]
        return live_hosts

    def enable_protection(self):
        sp.Popen(['arptables', '-F'])
        if self.isfedora:
            print "This is a RedHat based distro "
            sp.Popen(['arptables', '-P', 'IN', 'DROP'])
            sp.Popen(['arptables', '-P', 'OUT', 'DROP'])
            sp.Popen(['arptables', '-A', 'IN', '-s', self.gwip, '--source-hw', self.gwhw, '-j', 'ACCEPT'])
            sp.Popen(['arptables', '-A', 'OUT', '-d', self.gwip, '--target-hw', self.gwhw, '-j', 'ACCEPT'])
        else:
            print "This is not a RedHat based distro"
            sp.Popen(['arptables', '-P', 'INPUT', 'DROP'])
            sp.Popen(['arptables', '-P', 'OUTPUT', 'DROP'])
            sp.Popen(['arptables', '-A', 'INPUT', '-s', self.gwip, '--source-mac', self.gwhw, '-j', 'ACCEPT'])
            sp.Popen(['arptables', '-A', 'OUTPUT', '-d', self.gwip, '--destination-mac', self.gwhw, '-j', 'ACCEPT'])
            sp.Popen(['arp', '-s', self.gwip, self.gwhw])

    def disable_protection(self):
        if self.isfedora:
            sp.Popen(['arptables', '-P', 'IN', 'ACCEPT'])
            sp.Popen(['arptables', '-P', 'OUT', 'ACCEPT'])
        else:
            sp.Popen(['arptables', '-P', 'INPUT', 'ACCEPT'])
            sp.Popen(['arptables', '-P', 'OUTPUT', 'ACCEPT'])
        sp.Popen(['arptables', '-F'])