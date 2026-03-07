import requests
import urllib3
import json
urllib3.disable_warnings()

from config import ND_URL
from auth import get_token, get_headers

def create_vrf(fabric_name, vrf_name, vrf_id, vlan_id):
    token = get_token()
    url   = f"{ND_URL}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/top-down/fabrics/{fabric_name}/vrfs"

    vrf_template_config = json.dumps({
        "vrfVlanId":      str(vlan_id),
        "vrfVlanName":    vrf_name,
        "vrfDescription": f"VRF cree en stage PFE - {vrf_name}",
        "vrfRouteMap":    "FABRIC-RMAP-REDIST-SUBNET",
        "maxBGWAllowed":  "0",
        "advertiseHostRouteFlag": "false",
        "advertiseDefaultRouteFlag": "true",
        "configureStaticDefaultRouteFlag": "true"
    })

    payload = {
        "fabric":                   fabric_name,
        "vrfName":                  vrf_name,
        "vrfId":                    vrf_id,
        "vrfTemplate":              "Default_VRF_Universal",
        "vrfTemplateConfig":        vrf_template_config,
        "vrfExtensionTemplate":     "Default_VRF_Extension_Universal",
        "vrfExtensionTemplateConfig": "{}"
    }

    resp = requests.post(url, headers=get_headers(token), json=payload, verify=False)
    if resp.status_code in [200, 201]:
        print(f"[CREATE VRF] '{vrf_name}' créé avec succès")
    else:
        print(f"[CREATE VRF] Erreur {resp.status_code} : {resp.text[:300]}")
    return resp

def create_network(fabric_name, network_name, vlan_id, vrf_name, gateway_ip):
    token = get_token()
    url   = f"{ND_URL}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/top-down/fabrics/{fabric_name}/networks"

    # ⚠️ networkTemplateConfig doit être une STRING JSON pas un objet
    network_template_config = json.dumps({
        "vlanId":               str(vlan_id),
        "vlanName":             network_name,
        "gatewayIpAddress":     gateway_ip,
        "vrf":                  vrf_name,
        "suppressArp":          "false",
        "enableIR":             "false",
        "mcastGroup":           "",
        "dhcpServerAddr1":      "",
        "vrfDhcp":              "",
        "loopbackId":           "",
        "tag":                  "12345",
        "isLayer2Only":         "false",
        "nveId":                "1"
    })

    payload = {
        "fabric":                      fabric_name,
        "networkName":                 network_name,
        "networkTemplate":             "Default_Network_Universal",
        "networkTemplateConfig":       network_template_config,
        "networkExtensionTemplate":    "Default_Network_Extension_Universal",
        "networkExtensionTemplateConfig": "{}",
        "vrf":                         vrf_name
    }

    resp = requests.post(url, headers=get_headers(token), json=payload, verify=False)
    if resp.status_code in [200, 201]:
        print(f"[CREATE NETWORK] '{network_name}' créé (VLAN: {vlan_id})")
    else:
        print(f"[CREATE NETWORK] Erreur {resp.status_code} : {resp.text[:300]}")
    return resp

def delete_network(fabric_name, network_name):
    token = get_token()
    url   = f"{ND_URL}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/top-down/fabrics/{fabric_name}/networks/{network_name}"
    resp  = requests.delete(url, headers=get_headers(token), verify=False)
    if resp.status_code in [200, 204]:
        print(f"[DELETE NETWORK] '{network_name}' supprimé")
    else:
        print(f"[DELETE NETWORK] Erreur {resp.status_code} : {resp.text[:300]}")
    return resp

def delete_vrf(fabric_name, vrf_name):
    token = get_token()
    url   = f"{ND_URL}/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/top-down/fabrics/{fabric_name}/vrfs/{vrf_name}"
    resp  = requests.delete(url, headers=get_headers(token), verify=False)
    if resp.status_code in [200, 204]:
        print(f"[DELETE VRF] '{vrf_name}' supprimé")
    else:
        print(f"[DELETE VRF] Erreur {resp.status_code} : {resp.text[:300]}")
    return resp
