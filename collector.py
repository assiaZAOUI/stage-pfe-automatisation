import requests
import urllib3
import json
urllib3.disable_warnings()

from config import ND_URL
from auth import get_token, get_headers

def get_fabrics():
    token = get_token()
    url   = f"{ND_URL}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/control/fabrics"
    resp  = requests.get(url, headers=get_headers(token), verify=False)

    if resp.status_code != 200:
        print(f" get_fabrics : {resp.status_code} → {resp.text[:200]}")
        return []

    fabrics = resp.json()
    print(f"\n{'='*50}")
    print(f"  FABRICS ({len(fabrics)} trouvés)")
    print(f"{'='*50}")
    for f in fabrics:
        print(f"  • {f.get('fabricName','?')}  |  Type: {f.get('fabricType','?')}")
    return fabrics

def get_switches(fabric_name):
    token = get_token()
    url   = f"{ND_URL}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/inventory/allswitches?fabric={fabric_name}"
    resp  = requests.get(url, headers=get_headers(token), verify=False)

    if resp.status_code != 200:
        print(f" get_switches : {resp.status_code}")
        return []

    switches = resp.json()
    print(f"\n{'='*50}")
    print(f"  SWITCHES dans '{fabric_name}' ({len(switches)} trouvés)")
    print(f"{'='*50}")
    for sw in switches:
        print(f"  • {sw.get('logicalName','?'):<15} | IP: {sw.get('ipAddress','?'):<15} | Role: {sw.get('switchRole','?')}")
    return switches

def get_vrfs(fabric_name):
    token = get_token()
    url   = f"{ND_URL}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/top-down/fabrics/{fabric_name}/vrfs"
    resp  = requests.get(url, headers=get_headers(token), verify=False)

    if resp.status_code != 200:
        print(f" get_vrfs : {resp.status_code}")
        return []

    vrfs = resp.json()
    print(f"\n{'='*50}")
    print(f"  VRFs dans '{fabric_name}' ({len(vrfs)} trouvés)")
    print(f"{'='*50}")
    for vrf in vrfs:
        print(f"  • {vrf.get('vrfName','?'):<20} | ID: {vrf.get('vrfId','?'):<8} | Status: {vrf.get('vrfStatus','?')}")
    return vrfs

def get_networks(fabric_name):
    token = get_token()
    url   = f"{ND_URL}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/top-down/fabrics/{fabric_name}/networks"
    resp  = requests.get(url, headers=get_headers(token), verify=False)

    if resp.status_code != 200:
        print(f" get_networks : {resp.status_code}")
        return []

    networks = resp.json()
    print(f"\n{'='*50}")
    print(f"  NETWORKS dans '{fabric_name}' ({len(networks)} trouvés)")
    print(f"{'='*50}")
    for net in networks:
        name   = str(net.get('networkName') or '?')
        status = str(net.get('networkStatus') or 'NA')
        try:
            config = json.loads(net.get('networkTemplateConfig', '{}'))
            vlan   = str(config.get('vlanId') or '?')
        except:
            vlan = '?'
        print(f"  • {name:<25} | VLAN: {vlan:<6} | Status: {status}")
    return networks

def export_inventory_to_json(fabric_name, output_file="inventory.json"):
    data = {
        "fabric":    fabric_name,
        "switches":  get_switches(fabric_name),
        "vrfs":      get_vrfs(fabric_name),
        "networks":  get_networks(fabric_name)
    }
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\n Inventaire exporté dans '{output_file}'")
    return data
