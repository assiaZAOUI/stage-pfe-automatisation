import requests
import urllib3
import time
urllib3.disable_warnings()

from config import APIC_URL, USERNAME, PASSWORD

_token      = None
_token_time = 0
TOKEN_TTL   = 500  # Renouvellement avant expiration (600s)

def get_token(force_refresh=False):
    global _token, _token_time

    if force_refresh or not _token or (time.time() - _token_time > TOKEN_TTL):
        url = f"{APIC_URL}/api/aaaLogin.json"

        # ── Payload APIC — structure différente de Nexus Dashboard ──
        payload = {
            "aaaUser": {
                "attributes": {
                    "name": USERNAME,
                    "pwd" : PASSWORD
                }
            }
        }

        try:
            resp = requests.post(url, json=payload, verify=False, timeout=15)
            resp.raise_for_status()

            # ── Clé "aaaLogin" propre à APIC ──
            apic_data   = resp.json()["imdata"][0]["aaaLogin"]["attributes"]
            _token      = apic_data["token"]
            _token_time = time.time()

            print(f"[AUTH APIC] Token obtenu")
            print(f"  Version APIC : {apic_data['version']}")
            print(f"  Expiration   : {apic_data['refreshTimeoutSeconds']}s")
            print(f"  Token        : {_token[:50]}...")

        except Exception as e:
            print(f"[ERREUR AUTH] {e}")
            return None

    return _token

def get_headers(token):
    # ── APIC utilise Cookie et non Authorization Bearer ──
    return {
        "Cookie"      : f"APIC-cookie={token}",
        "Content-Type": "application/json"
    }
