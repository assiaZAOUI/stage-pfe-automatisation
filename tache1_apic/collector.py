import requests
import urllib3
import json
urllib3.disable_warnings()

from config import APIC_URL
from auth import get_token, get_headers

def get_tenants():
    token = get_token()
    url   = f"{APIC_URL}/api/node/class/fvTenant.json"
    resp  = requests.get(url, headers=get_headers(token), verify=False)
    data  = resp.json()["imdata"]
    print(f"\n{'='*50}")
    print(f"  TENANTS ({len(data)} trouvés)")
    print(f"{'='*50}")
    for item in data:
        attr = item["fvTenant"]["attributes"]
        print(f"  • {attr['name']:<20} | DN: {attr['dn']}")
    return data

def get_vrfs():
    token = get_token()
    url   = f"{APIC_URL}/api/node/class/fvCtx.json"
    resp  = requests.get(url, headers=get_headers(token), verify=False)
    data  = resp.json()["imdata"]
    print(f"\n{'='*50}")
    print(f"  VRFs — fvCtx ({len(data)} trouvés)")
    print(f"{'='*50}")
    for item in data:
        attr = item["fvCtx"]["attributes"]
        print(f"  • {attr['name']:<20} | DN: {attr['dn']}")
    return data

def get_bridge_domains():
    token = get_token()
    url   = f"{APIC_URL}/api/node/class/fvBD.json"
    resp  = requests.get(url, headers=get_headers(token), verify=False)
    data  = resp.json()["imdata"]
    print(f"\n{'='*50}")
    print(f"  BRIDGE DOMAINS — fvBD ({len(data)} trouvés)")
    print(f"{'='*50}")
    for item in data:
        attr = item["fvBD"]["attributes"]
        print(f"  • {attr['name']:<20} | DN: {attr['dn']}")
    return data

def get_epgs():
    token = get_token()
    url   = f"{APIC_URL}/api/node/class/fvAEPg.json"
    resp  = requests.get(url, headers=get_headers(token), verify=False)
    data  = resp.json()["imdata"]
    print(f"\n{'='*50}")
    print(f"  EPGs — fvAEPg ({len(data)} trouvés)")
    print(f"{'='*50}")
    for item in data:
        attr = item["fvAEPg"]["attributes"]
        print(f"  • {attr['name']:<20} | DN: {attr['dn']}")
    return data

def get_nodes():
    token = get_token()
    url   = f"{APIC_URL}/api/node/class/topSystem.json"
    resp  = requests.get(url, headers=get_headers(token), verify=False)
    data  = resp.json()["imdata"]
    print(f"\n{'='*50}")
    print(f"  NODES ACI ({len(data)} trouvés)")
    print(f"{'='*50}")
    for item in data:
        attr = item["topSystem"]["attributes"]
        print(f"  • {attr['name']:<15} | Role: {attr['role']:<10} | IP: {attr['address']}")
    return data

def export_inventory(output_file="inventaire_apic_avant.json"):
    print(f"\n Export inventaire en cours...")
    data = {
        "apic_url"      : APIC_URL,
        "tenants"       : get_tenants(),
        "vrfs"          : get_vrfs(),
        "bridge_domains": get_bridge_domains(),
        "epgs"          : get_epgs(),
        "nodes"         : get_nodes()
    }
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Inventaire exporté dans '{output_file}'")
    return data
