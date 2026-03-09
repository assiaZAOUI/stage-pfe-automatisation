import requests, urllib3, json
urllib3.disable_warnings()

APIC_URL = "https://sandboxapicdc.cisco.com"
USERNAME = "admin"
PASSWORD = "!v3G@!4@Y"

def get_token():
    resp = requests.post(f"{APIC_URL}/api/aaaLogin.json",
        json={"aaaUser": {"attributes": {"name": USERNAME, "pwd": PASSWORD}}},
        verify=False)
    return resp.json()["imdata"][0]["aaaLogin"]["attributes"]["token"]

token = get_token()
headers = {"Cookie": f"APIC-cookie={token}", "Content-Type": "application/json"}

# Test 1 — MSO/NDO Sites
print("\n── Test NDO Sites ──")
r1 = requests.get(f"{APIC_URL}/mso/api/v1/sites", headers=headers, verify=False)
print(f"Status : {r1.status_code} | {r1.text[:200]}")

# Test 2 — NDO Schemas
print("\n── Test NDO Schemas ──")
r2 = requests.get(f"{APIC_URL}/mso/api/v1/schemas", headers=headers, verify=False)
print(f"Status : {r2.status_code} | {r2.text[:200]}")

# Test 3 — NDO Tenants
print("\n── Test NDO Tenants ──")
r3 = requests.get(f"{APIC_URL}/mso/api/v1/tenants", headers=headers, verify=False)
print(f"Status : {r3.status_code} | {r3.text[:200]}")