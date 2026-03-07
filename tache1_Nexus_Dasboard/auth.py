import requests
import urllib3
import time
urllib3.disable_warnings()

from config import ND_URL, USERNAME, PASSWORD

_token      = None
_token_time = 0
TOKEN_TTL   = 500

def get_token(force_refresh=False):
    global _token, _token_time

    if force_refresh or not _token or (time.time() - _token_time > TOKEN_TTL):
        url     = f"{ND_URL}/login"
        payload = {
            "userName":   USERNAME,
            "userPasswd": PASSWORD,
            "domain":     "local"
        }
        try:
            resp = requests.post(url, json=payload, verify=False, timeout=10)
            resp.raise_for_status()
            _token      = resp.json()["jwttoken"]
            _token_time = time.time()
            print("[AUTH] Token obtenu avec succès")
        except Exception as e:
            print(f"[ERREUR AUTH] {e}")
            return None

    return _token

def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json"
    }
