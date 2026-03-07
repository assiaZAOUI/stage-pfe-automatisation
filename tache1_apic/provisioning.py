import requests
import urllib3
urllib3.disable_warnings()

from config import APIC_URL
#from config import ND_URL
from auth import get_token, get_headers

# ─────────────────────────────────────────────────────────────
#  TÂCHE 1 (ancienne) — Nexus Dashboard NDFC

# def create_vrf(fabric_name, vrf_name, vrf_id, vlan_id):
#     url = f"{BASE}/top-down/fabrics/{fabric_name}/vrfs"
#     vrf_template_config = json.dumps({
#         "vrfVlanId"  : str(vlan_id),
#         "vrfVlanName": vrf_name,
#         "vrfSegmentId": str(vrf_id),
#     })
#     payload = {
#         "fabric"             : fabric_name,
#         "vrfName"            : vrf_name,
#         "vrfId"              : vrf_id,
#         "vrfTemplate"        : "Default_VRF_Universal",
#         "vrfTemplateConfig"  : vrf_template_config,   # ← STRING obligatoire !
#     }
#     resp = requests.post(url, headers=get_headers(get_token()), json=payload, verify=False)
#     print(f"[CREATE VRF] {vrf_name} → {resp.status_code}")

# def create_network(fabric_name, network_name, vlan_id, vrf_name, gateway_ip):
#     url = f"{BASE}/top-down/fabrics/{fabric_name}/networks"
#     payload = { ... }
#     resp = requests.post(url, headers=get_headers(get_token()), json=payload, verify=False)
#     print(f"[CREATE NETWORK] {network_name} → {resp.status_code}")

# def delete_network(fabric_name, network_name):
#     url = f"{BASE}/top-down/fabrics/{fabric_name}/networks/{network_name}"
#     resp = requests.delete(url, headers=get_headers(get_token()), verify=False)
#     print(f"[DELETE NETWORK] {network_name} → {resp.status_code}")

# def delete_vrf(fabric_name, vrf_name):
#     url = f"{BASE}/top-down/fabrics/{fabric_name}/vrfs/{vrf_name}"
#     resp = requests.delete(url, headers=get_headers(get_token()), verify=False)
#     print(f"[DELETE VRF] {vrf_name} → {resp.status_code}")

# ─────────────────────────────────────────────────────────────
#  TÂCHE 1 (nouvelle) — Cisco APIC
# ─────────────────────────────────────────────────────────────

def create_tenant(tenant_name, description=""):
    token   = get_token()
    url     = f"{APIC_URL}/api/node/mo/uni/tn-{tenant_name}.json"
    payload = {
        "fvTenant": {
            "attributes": {
                "name"  : tenant_name,
                "descr" : description,
                "status": "created"
            }
        }
    }
    resp   = requests.post(url, headers=get_headers(token), json=payload, verify=False)
    status = "OK" if resp.status_code == 200 else f"❌ {resp.status_code} — {resp.text[:100]}"
    print(f"[CREATE TENANT] '{tenant_name}' → {status}")
    return resp

def create_vrf(tenant_name, vrf_name):
    token   = get_token()
    url     = f"{APIC_URL}/api/node/mo/uni/tn-{tenant_name}/ctx-{vrf_name}.json"
    payload = {
        "fvCtx": {
            "attributes": {
                "name"  : vrf_name,
                "descr" : f"VRF créé en stage PFE — {vrf_name}",
                "status": "created"
            }
        }
    }
    resp   = requests.post(url, headers=get_headers(token), json=payload, verify=False)
    status = "OK" if resp.status_code == 200 else f"❌ {resp.status_code} — {resp.text[:100]}"
    print(f"[CREATE VRF] '{vrf_name}' dans '{tenant_name}' → {status}")
    return resp

def create_bridge_domain(tenant_name, bd_name, vrf_name):
    token   = get_token()
    url     = f"{APIC_URL}/api/node/mo/uni/tn-{tenant_name}/BD-{bd_name}.json"
    payload = {
        "fvBD": {
            "attributes": {
                "name"  : bd_name,
                "descr" : f"Bridge Domain créé en stage PFE — {bd_name}",
                "status": "created"
            },
            # ── Liaison BD → VRF via fvRsCtx ──
            "children": [{
                "fvRsCtx": {
                    "attributes": {
                        "tnFvCtxName": vrf_name
                    }
                }
            }]
        }
    }
    resp   = requests.post(url, headers=get_headers(token), json=payload, verify=False)
    status = "OK" if resp.status_code == 200 else f"❌ {resp.status_code} — {resp.text[:100]}"
    print(f"[CREATE BD] '{bd_name}' lié à VRF '{vrf_name}' → {status}")
    return resp

def create_ap(tenant_name, ap_name):
    token   = get_token()
    url     = f"{APIC_URL}/api/node/mo/uni/tn-{tenant_name}/ap-{ap_name}.json"
    payload = {
        "fvAp": {
            "attributes": {
                "name"  : ap_name,
                "descr" : f"Application Profile créé en stage PFE",
                "status": "created"
            }
        }
    }
    resp   = requests.post(url, headers=get_headers(token), json=payload, verify=False)
    status = "OK" if resp.status_code == 200 else f"❌ {resp.status_code} — {resp.text[:100]}"
    print(f"[CREATE AP] '{ap_name}' dans '{tenant_name}' → {status}")
    return resp

def create_epg(tenant_name, ap_name, epg_name, bd_name):
    token   = get_token()
    url     = f"{APIC_URL}/api/node/mo/uni/tn-{tenant_name}/ap-{ap_name}/epg-{epg_name}.json"
    payload = {
        "fvAEPg": {
            "attributes": {
                "name"  : epg_name,
                "descr" : f"EPG créé en stage PFE — {epg_name}",
                "status": "created"
            },
            # ── Liaison EPG → Bridge Domain via fvRsBd ──
            "children": [{
                "fvRsBd": {
                    "attributes": {
                        "tnFvBDName": bd_name
                    }
                }
            }]
        }
    }
    resp   = requests.post(url, headers=get_headers(token), json=payload, verify=False)
    status = "OK" if resp.status_code == 200 else f"❌ {resp.status_code} — {resp.text[:100]}"
    print(f"[CREATE EPG] '{epg_name}' dans AP '{ap_name}' lié à BD '{bd_name}' → {status}")
    return resp

def delete_tenant(tenant_name):
    # ── APIC : DELETE via POST avec status="deleted" ──
    # ── Supprimer le Tenant supprime automatiquement tous ses enfants ──
    token   = get_token()
    url     = f"{APIC_URL}/api/node/mo/uni/tn-{tenant_name}.json"
    payload = {
        "fvTenant": {
            "attributes": {
                "name"  : tenant_name,
                "status": "deleted"
            }
        }
    }
    resp   = requests.post(url, headers=get_headers(token), json=payload, verify=False)
    status = "Supprimé" if resp.status_code == 200 else f"❌ {resp.status_code} — {resp.text[:100]}"
    print(f"[DELETE TENANT] '{tenant_name}' + tous ses enfants → {status}")
    return resp