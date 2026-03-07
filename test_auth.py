import requests
import urllib3
urllib3.disable_warnings()

from config import ND_URL, USERNAME, PASSWORD

def get_token():
    url = f"{ND_URL}/login"
    payload = {
        "userName": USERNAME,
        "userPasswd": PASSWORD,
        "domain": "local"
    }
    resp = requests.post(url, json=payload, verify=False, timeout=10)
    print(f"Status : {resp.status_code}")
    print(f"Réponse : {resp.text[:200]}")

get_token()
