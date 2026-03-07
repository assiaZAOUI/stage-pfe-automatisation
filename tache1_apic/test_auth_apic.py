import requests
import urllib3
import json
urllib3.disable_warnings()

APIC_URL = "https://sandboxapicdc.cisco.com"
USERNAME = "admin"
PASSWORD = "!v3G@!4@Y"

def get_token():
    url = f"{APIC_URL}/api/aaaLogin.json"
    payload = {
        "aaaUser": {
            "attributes": {
                "name": USERNAME,
                "pwd": PASSWORD
            }
        }
    }
    resp = requests.post(url, json=payload, verify=False, timeout=15)

    # APIC retourne "aaaLogin"
    token = resp.json()["imdata"][0]["aaaLogin"]["attributes"]["token"]
    print(f"[AUTH APIC] Token obtenu !")
    print(f"Version APIC : {resp.json()['imdata'][0]['aaaLogin']['attributes']['version']}")
    print(f"Token        : {token[:50]}...")
    return token

def get_headers(token):
    return {
        "Cookie"      : f"APIC-cookie={token}",
        "Content-Type": "application/json"
    }

token = get_token()