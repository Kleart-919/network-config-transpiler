"""
Vendor Templates

This module stores vendor-specific rendering templates.

The goal is to gradually move syntax rules out of hardcoded generator logic
and into reusable vendor metadata.
"""


VENDOR_TEMPLATES = {
    "cisco_ios": {
        "hostname": "hostname {hostname}",
        "vlan": "vlan {vlan_id}",
        "vlan_name": " name {vlan_name}",
        "interface": "interface {interface_name}",
        "interface_description": " description {description}",
        "access_mode": " switchport mode access",
        "access_vlan": " switchport access vlan {vlan_id}",
        "trunk_mode": " switchport mode trunk",
        "allowed_vlans": " switchport trunk allowed vlan {vlans}",
    },
    "juniper_junos": {
        "hostname": "set system host-name {hostname}",
        "vlan": "set vlans {vlan_name} vlan-id {vlan_id}",
        "interface_description": 'set interfaces {interface_name} description "{description}"',
        "access_mode": "set interfaces {interface_name} unit 0 family ethernet-switching interface-mode access",
        "access_vlan": "set interfaces {interface_name} unit 0 family ethernet-switching vlan members {vlan_name}",
        "trunk_mode": "set interfaces {interface_name} unit 0 family ethernet-switching interface-mode trunk",
        "allowed_vlans": "set interfaces {interface_name} unit 0 family ethernet-switching vlan members [ {vlans} ]",
    },
}