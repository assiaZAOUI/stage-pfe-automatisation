# Objets collectés dans MSO/NDO :
#   - Sites     : les fabrics ACI enregistrés dans MSO
#   - Tenants   : les tenants gérés par MSO
#   - Schemas   : collections de Templates contenant les politiques
#   - Templates : VRF, BD, ANP, EPG définis dans chaque Schema
#
# Pattern URL MSO :
#   GET /api/v1/sites          → liste des sites ACI
#   GET /api/v1/tenants        → liste des tenants
#   GET /api/v1/schemas        → liste des schemas
#   GET /api/v1/schemas/{id}   → détail d'un schema (templates + objets)
# ============================================================

import requests
import urllib3
import json
from auth import get_headers
from config import MSO_URL

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ── 1. SITES ────────────────────────────────────────────────
def get_sites():
    """
    Récupère la liste des sites ACI enregistrés dans MSO.
    Un site = un fabric ACI avec son APIC.
    """
    url  = f"{MSO_URL}/api/v1/sites"
    resp = requests.get(url, headers=get_headers(), verify=False, timeout=30)

    if resp.status_code != 200:
        raise Exception(f"[ERREUR get_sites] Status {resp.status_code} — {resp.text[:200]}")

    sites = resp.json().get("sites", [])
    print(f"\n  ── Sites MSO ({len(sites)}) ──")
    for s in sites:
        print(f"  • {s.get('name','?'):<25} | ID: {s.get('id','?'):<36} | Status: {s.get('operationalStatus','?')}")
    return sites


# ── 2. TENANTS ──────────────────────────────────────────────
def get_tenants():
    """
    Récupère la liste des tenants gérés par MSO.
    Ces tenants sont synchronisés sur tous les sites associés.
    """
    url  = f"{MSO_URL}/api/v1/tenants"
    resp = requests.get(url, headers=get_headers(), verify=False, timeout=30)

    if resp.status_code != 200:
        raise Exception(f"[ERREUR get_tenants] Status {resp.status_code} — {resp.text[:200]}")

    tenants = resp.json().get("tenants", [])
    print(f"\n  ── Tenants MSO ({len(tenants)}) ──")
    for t in tenants:
        sites_assoc = [s.get("siteName","?") for s in t.get("siteAssociations", [])]
        print(f"  • {t.get('name','?'):<25} | ID: {t.get('id','?'):<36} | Sites: {', '.join(sites_assoc) or 'aucun'}")
    return tenants


# ── 3. SCHEMAS ──────────────────────────────────────────────
def get_schemas():
    """
    Récupère la liste des Schemas MSO.
    Un Schema = conteneur de Templates qui définissent les politiques réseau.
    """
    url  = f"{MSO_URL}/api/v1/schemas"
    resp = requests.get(url, headers=get_headers(), verify=False, timeout=30)

    if resp.status_code != 200:
        raise Exception(f"[ERREUR get_schemas] Status {resp.status_code} — {resp.text[:200]}")

    schemas = resp.json().get("schemas", [])
    print(f"\n  ── Schemas MSO ({len(schemas)}) ──")
    for sc in schemas:
        templates = sc.get("templates", [])
        print(f"  • {sc.get('displayName','?'):<25} | ID: {sc.get('id','?'):<36} | Templates: {len(templates)}")
    return schemas


# ── 4. DÉTAIL D'UN SCHEMA ───────────────────────────────────
def get_schema_detail(schema_id):
    """
    Récupère le détail complet d'un Schema :
    Templates, VRFs, BDs, ANPs, EPGs.
    """
    url  = f"{MSO_URL}/api/v1/schemas/{schema_id}"
    resp = requests.get(url, headers=get_headers(), verify=False, timeout=30)

    if resp.status_code != 200:
        raise Exception(f"[ERREUR get_schema_detail] Status {resp.status_code} — {resp.text[:200]}")

    schema = resp.json()
    print(f"\n  ── Détail Schema : {schema.get('displayName','?')} ──")

    for tmpl in schema.get("templates", []):
        print(f"\n    Template : {tmpl.get('displayName','?')} (Tenant: {tmpl.get('tenantId','?')})")
        print(f"      VRFs     : {len(tmpl.get('vrfs', []))}")
        print(f"      BDs      : {len(tmpl.get('bds', []))}")
        print(f"      ANPs     : {len(tmpl.get('anps', []))}")
        print(f"      Contracts: {len(tmpl.get('contracts', []))}")

        for anp in tmpl.get("anps", []):
            epgs = anp.get("epgs", [])
            print(f"      ANP '{anp.get('displayName','?')}' → {len(epgs)} EPG(s)")
            for epg in epgs:
                print(f"        EPG: {epg.get('displayName','?')}")

    return schema


# ── 5. VERSION MSO ──────────────────────────────────────────
def get_version():
    """Récupère la version du MSO/NDO installé."""
    url  = f"{MSO_URL}/api/v1/platform/version"
    resp = requests.get(url, headers=get_headers(), verify=False, timeout=30)

    if resp.status_code != 200:
        raise Exception(f"[ERREUR get_version] Status {resp.status_code} — {resp.text[:200]}")

    data = resp.json()
    print(f"\n  ── Version MSO/NDO ──")
    print(f"  Version : {data.get('version','?')}")
    print(f"  Build   : {data.get('buildTime','?')}")
    return data


# ── 6. EXPORT INVENTAIRE JSON ───────────────────────────────
def export_inventory(output_file):
    """
    Collecte complète et export en JSON.
    Capture l'état AVANT provisioning.
    """
    print(f"\n{'='*60}")
    print(f"  COLLECTE INVENTAIRE MSO/NDO")
    print(f"{'='*60}")

    inventaire = {
        "source":    "Cisco MSO/NDO REST API",
        "sandbox":   MSO_URL,
        "version":   {},
        "sites":     [],
        "tenants":   [],
        "schemas":   [],
    }

    try:
        inventaire["version"] = get_version()
    except Exception as e:
        print(f"  [WARN] Version : {e}")

    try:
        inventaire["sites"] = get_sites()
    except Exception as e:
        print(f"  [WARN] Sites : {e}")

    try:
        inventaire["tenants"] = get_tenants()
    except Exception as e:
        print(f"  [WARN] Tenants : {e}")

    try:
        schemas = get_schemas()
        # Récupérer le détail de chaque schema
        schemas_detail = []
        for sc in schemas:
            try:
                detail = get_schema_detail(sc["id"])
                schemas_detail.append(detail)
            except Exception as e:
                print(f"  [WARN] Détail schema {sc.get('id')} : {e}")
        inventaire["schemas"] = schemas_detail
    except Exception as e:
        print(f"  [WARN] Schemas : {e}")

    # Export JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(inventaire, f, indent=2, ensure_ascii=False)

    print(f"\n  Inventaire exporté → {output_file}")
    print(f"     Sites   : {len(inventaire['sites'])}")
    print(f"     Tenants : {len(inventaire['tenants'])}")
    print(f"     Schemas : {len(inventaire['schemas'])}")

    return inventaire


if __name__ == "__main__":
    export_inventory("inventaire_mso_avant.json")