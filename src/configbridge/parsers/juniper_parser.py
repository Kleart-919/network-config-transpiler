"""
Juniper Parser

Version 1 parser for Juniper Junos set-style Layer 2 configurations.
"""

import shlex

from configbridge.models.intent_model import IntentModel, VLAN, Interface


class JuniperParser:
    """
    Juniper Junos set-style parser.

    Reads Junos set commands and produces an IntentModel.
    """

    def parse(self, config_text: str) -> IntentModel:
        intent = IntentModel()
        interfaces_by_name = {}
        vlan_ids_by_name = {}

        lines = config_text.splitlines()

        for raw_line in lines:
            line = raw_line.strip()

            if not line or not line.startswith("set "):
                continue

            parts = shlex.split(line)

            if len(parts) < 2:
                continue

            if parts[:3] == ["set", "system", "host-name"] and len(parts) >= 4:
                intent.hostname = parts[3]
                continue

            if len(parts) >= 5 and parts[:2] == ["set", "vlans"]:
                vlan_name = parts[2]

                if parts[3] == "vlan-id":
                    vlan_id = int(parts[4])
                    vlan_ids_by_name[vlan_name] = vlan_id
                    intent.vlans.append(VLAN(vlan_id=vlan_id, name=vlan_name))
                    continue

            if len(parts) >= 4 and parts[:2] == ["set", "interfaces"]:
                interface_name = parts[2]

                if interface_name not in interfaces_by_name:
                    interfaces_by_name[interface_name] = Interface(name=interface_name)
                    intent.interfaces.append(interfaces_by_name[interface_name])

                interface = interfaces_by_name[interface_name]

                if len(parts) >= 5 and parts[3] == "description":
                    interface.description = parts[4]
                    continue

                if "interface-mode" in parts:
                    mode_index = parts.index("interface-mode")
                    if mode_index + 1 < len(parts):
                        interface.mode = parts[mode_index + 1]
                    continue

                if "vlan" in parts and "members" in parts:
                    members_index = parts.index("members")
                    members = parts[members_index + 1:]

                    cleaned_members = [
                        member
                        for member in members
                        if member not in ["[", "]"]
                    ]

                    if interface.mode == "access" and cleaned_members:
                        vlan_name = cleaned_members[0]
                        interface.access_vlan = vlan_ids_by_name.get(vlan_name)

                    if interface.mode == "trunk":
                        interface.allowed_vlans = [
                            vlan_ids_by_name[vlan_name]
                            for vlan_name in cleaned_members
                            if vlan_name in vlan_ids_by_name
                        ]

        return intent