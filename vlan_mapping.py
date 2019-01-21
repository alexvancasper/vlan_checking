#!/usr/bin/env python

from __future__ import print_function
import re

def composition_vlans(init):
    def next_item(arr):
        for item in arr:
            yield item

    myinit = next_item(init)
    k=myinit.next()
    outline=""
    new_range=True
    while k>0:
        try:
            new=myinit.next()
        except StopIteration:
            outline+=str(init[-1])
            break
        if new - k != 1:
            outline+="{},".format(k)
            new_range=True
        else:
            if new_range:
                outline+="{}-".format(k)
                new_range=False
        k=new
    return outline

def decomposition_vlans(deinit):
    OUT=[]
    def print_vlans(deinit, attr):
        if attr == "commaonly":
            out = deinit.split(",")
            for id in out:
                OUT.append(int(id))
        if attr == "dashonly":
            out = deinit.split("-")
            for id in range(int(out[0]),int(out[1])+1):
                OUT.append(int(id))
        if attr == "none":
            OUT.append(int(deinit))
        return

    if "," not in deinit and "-" not in deinit:
        print_vlans(deinit,"none")
    if "," in deinit and '-' not in deinit:
        print_vlans(deinit, "commaonly")
    if "," not in deinit and "-" in deinit:
        print_vlans(deinit, "dashonly")

    if "," in deinit and "-" in deinit:
        out = deinit.split(",")
        if len(out)>0:
            for item in out:
                if "," not in item and "-" not in item:
                    print_vlans(item,"none")
                if "," in item and '-' not in item:
                    print_vlans(item, "commaonly")
                if "," not in item and "-" in item:
                    print_vlans(item, "dashonly")
    return OUT

def get_vlans_range_cfg(in_lines):
    switchport_cfg_pattern = re.compile(r"switchport\strunk\sallowed\svlan\s(\d+.*)")
    switchport_add_cfg_pattern = re.compile(r"switchport trunk allowed vlan add\s(\d+.*)")
    OUTPUT=[]
    for line in in_lines:
        switch_port_line = switchport_cfg_pattern.search(line)
        if switch_port_line:
            vlans_range = switch_port_line.group(1)
            OUTPUT.append(vlans_range)
        switchport_add_vlan = switchport_add_cfg_pattern.search(line)
        if switchport_add_vlan:
            add_vlan_range = switchport_add_vlan.group(1)
            OUTPUT.append(add_vlan_range)
    result=[]
    for item in OUTPUT:
        result.extend(decomposition_vlans(item))
    return result

def get_mapping_vlans(in_lines):
    translations_pattern = re.compile(r"switchport vlan mapping\s(\d+)\s(\d+)")
    OUTPUT = []
    for line in in_lines:
        translations = translations_pattern.search(line)
        if translations:
            OUTPUT.append(int(translations.group(2)))
    return OUTPUT

def get_config(in_lines):
    interface_line = re.compile(r"^\s{0,10}interface\s(.*)")
    delimeter_line = re.compile(r"^!$")
    switchport_cfg_pattern = re.compile(r"switchport\strunk\sallowed\svlan\s(\d+.*)")
    switchport_add_cfg_pattern = re.compile(r"switchport trunk allowed vlan add\s(\d+.*)")
    translations_pattern = re.compile(r"switchport vlan mapping\s(\d+)\s(\d+)")

    start_to_collect=False
    
    for line in in_lines:
        interface_name_tmp = interface_line.search(line)
        if interface_name_tmp:
            interface_name = interface_name_tmp.group(1)
            start_to_collect=True
            CFG_VLANS=[]
            MAPPED_VLANS=[]

        delimeter = delimeter_line.search(line)
        if delimeter:
            start_to_collect=False
            print("interface "+interface_name)

            cfg_vlans=[]
            for item in CFG_VLANS:
                cfg_vlans.extend(decomposition_vlans(item))

            UNMAPPED_VLAN=[]
            for vlan in MAPPED_VLANS:
                if vlan not in cfg_vlans:
                   UNMAPPED_VLAN.append(vlan)

            print("Configured vlans: "+str(len(cfg_vlans)))
            print("Mapped vlans:     "+str(len(MAPPED_VLANS)))

            if len(UNMAPPED_VLAN)>0:
                print("Unmapped vlans: ", end="")
                print(UNMAPPED_VLAN)
                print("\n")
            else:
                print("All is correct\n")

        if start_to_collect:
            switch_port_line = switchport_cfg_pattern.search(line)
            if switch_port_line:
                vlans_range = switch_port_line.group(1)
                CFG_VLANS.append(vlans_range)
            switchport_add_vlan = switchport_add_cfg_pattern.search(line)
            if switchport_add_vlan:
                add_vlan_range = switchport_add_vlan.group(1)
                CFG_VLANS.append(add_vlan_range)
            translations = translations_pattern.search(line)
            if translations:
                MAPPED_VLANS.append(int(translations.group(2)))            

def main():
    file1 = open("config.cfg",'r')
    in_lines = file1.readlines()
    file1.close()    
    if in_lines[-1] != "!":
        in_lines.extend(["!"])
    get_config(in_lines)



if __name__ == '__main__':
    main()
