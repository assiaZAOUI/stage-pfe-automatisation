# DIFFÉRENCES vs Tâche 1 :
#
#  Tâche 1 — Nexus Dashboard NDFC :
#    POST /login  → {"userName": ..., "userPasswd": ..., "domain": "local"}
#    Header       → Authorization: Bearer <jwttoken>
#
#  Tâche 1 — Cisco APIC :
#    POST /api/aaaLogin.json → {"aaaUser": {"attributes": {"name":..., "pwd":...}}}
#    Header                 → Cookie: APIC-cookie=<token>
#
#  Tâche 2 — MSO/NDO :
#    POST /api/v1/auth/login → {"username": ..., "password": ..., "domain": ...}
#    Header                 → Cookie: AuthCookie=<token>
#                          OU Authorization: Bearer <token>  (selon version NDO)
# ============================================================

import requests
import urllib3
import time
from config import MSO_URL, USERNAME, PASSWORD, LOGIN_DOMAIN

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Token en cache pour éviter les re-authentifications inutiles
_token_cache = {"token": None, "timestamp": 0}
TOKEN_TTL    = 500  # secondes — token MSO expire après 600s

def get_token():
    """
    Authentification MSO/NDO via POST /api/v1/auth/login
    Retourne le token JWT de session.
    """
    # Vérifier si le token en cache est encore valide
    if _token_cache["token"] and (time.time() - _token_cache["timestamp"]) < TOKEN_TTL:
        return _token_cache["token"]

    url = f"{MSO_URL}/api/v1/auth/login"

    payload = {
        "username": USERNAME,
        "password": PASSWORD,
        "domain":   LOGIN_DOMAIN   # "local" ou "DefaultAuth"
    }

    print(f"  [AUTH] POST {url}")
    resp = requests.post(url, json=payload, verify=False, timeout=30)

    if resp.status_code != 200:
        raise Exception(f"[ERREUR AUTH] Status {resp.status_code} — {resp.text[:200]}")

    # Le token se trouve dans la réponse JSON
    # Selon la version NDO : clé "token" ou "jwtToken"
    data  = resp.json()
    token = data.get("token") or data.get("jwtToken")

    if not token:
        raise Exception(f"[ERREUR AUTH] Token introuvable dans la réponse : {data}")

    # Mise en cache
    _token_cache["token"]     = token
    _token_cache["timestamp"] = time.time()

    print(f"  [AUTH] Token obtenu ({len(token)} chars)")
    return token


def get_headers():
    """
    Retourne les headers HTTP pour les requêtes MSO/NDO.
    MSO utilise Cookie: AuthCookie=<token>
    """
    token = get_token()
    return {
        "Cookie":       f"AuthCookie={token}",
        "Authorization": f"Bearer {token}",   # certaines versions NDO utilisent Bearer
        "Content-Type": "application/json"
    }


def test_auth():
    """Test complet de l'authentification"""
    print("\n" + "="*60)
    print("  TEST AUTHENTIFICATION MSO/NDO")
    print("="*60)
    print(f"  URL      : {MSO_URL}")
    print(f"  Username : {USERNAME}")
    print(f"  Domain   : {LOGIN_DOMAIN}")
    print("-"*60)

    try:
        token   = get_token()
        headers = get_headers()
        print(f"\n  Authentification réussie !")
        print(f"  Token (50 premiers chars) : {token[:50]}...")
        print(f"  Header Cookie : AuthCookie={token[:20]}...")
        return True
    except Exception as e:
        print(f"\n  Échec : {e}")
        return False


if __name__ == "__main__":
    test_auth()