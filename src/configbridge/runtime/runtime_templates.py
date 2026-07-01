"""
Runtime command templates.
"""

RUNTIME_TEMPLATES = {

    "Juniper Junos": {

        "configure.terminal": "configure",

        "show.system.version": "show version",

        "show.interfaces.status": "show interfaces terse",

        "show.vlan.brief": "show vlans",

        "interface.enter": "edit interfaces {interface}",

        "interface.description": 'set description "{value}"',

        "interface.shutdown": "set disable",

        "interface.no_shutdown": "delete disable",

        "interface.switchport.mode.access": (
            "set unit 0 family ethernet-switching interface-mode access"
        ),

        "interface.switchport.mode.trunk": (
            "set unit 0 family ethernet-switching interface-mode trunk"
        ),

        "interface.switchport.access.vlan": (
            "delete unit 0 family ethernet-switching vlan\n"
            "set unit 0 family ethernet-switching vlan members {vlan}"
        ),

        "mode.exit": "exit",

        "mode.end": "top",

    }

}