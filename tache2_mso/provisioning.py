# Ordre de création obligatoire dans MSO :
#   1. Tenant         → create_tenant()
#   2. Schema         → create_schema()
#   3. Template       → inclus dans create_schema()
#   4. VRF            → add_vrf_to_template()
#   5. BD             → add_bd_to_template()   (lié au VRF)
#   6. ANP            → add_anp_to_template()
#   7. EPG            → add_epg_to_template()  (lié au BD et ANP)
#   8. Deploy         → deploy_template()      → pousse sur les APICs
#   9. Suppression    → delete_schema() + delete_tenant()
#
# DIFFÉRENCE CLÉ vs APIC Tâche 1 :
#   APIC : chaque objet créé séparément avec son propre POST
#   MSO  : tous les objets (VRF, BD, EPG...) sont définis dans
#          un Schema via PATCH, puis déployés en une seule opération
# ============================================================

import requests
import urllib3
import json
from auth import get_headers
from config import (MSO_URL, SITE_NAME, TENANT_NAME,
                    SCHEMA_NAME, TEMPLATE_NAME,
                    VRF_NAME, BD_NAME, ANP_NAME, EPG_NAME)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ── 1. CRÉER UN TENANT ──────────────────────────────────────
def create_tenant(tenant_name, description="Stage PFE Automatisation"):
    """
    Crée un Tenant dans MSO.
    Le Tenant sera automatiquement propagé aux sites associés.
    """
    url     = f"{MSO_URL}/api/v1/tenants"
    payload = {
        "name":        tenant_name,
        "displayName": tenant_name,
        "description": description,
        "siteAssociations": [],   # on associe aux sites après
        "userAssociations":  [{"userId": "admin"}]
    }

    print(f"\n  [PROVISIONING] Création Tenant : {tenant_name}")
    resp = requests.post(url, headers=get_headers(), json=payload, verify=False, timeout=30)

    if resp.status_code not in [200, 201]:
        raise Exception(f"[ERREUR create_tenant] Status {resp.status_code} — {resp.text[:300]}")

    data      = resp.json()
    tenant_id = data.get("id")
    print(f"  Tenant '{tenant_name}' créé — ID: {tenant_id}")
    return tenant_id


# ── 2. CRÉER UN SCHEMA + TEMPLATE ───────────────────────────
def create_schema(schema_name, template_name, tenant_id):
    """
    Crée un Schema MSO avec un Template vide.
    Le Schema est le conteneur principal des politiques réseau dans MSO.
    Un Schema peut contenir plusieurs Templates.
    """
    url     = f"{MSO_URL}/api/v1/schemas"
    payload = {
        "displayName": schema_name,
        "templates": [
            {
                "name":        template_name,
                "displayName": template_name,
                "tenantId":    tenant_id,
                "anps":        [],
                "vrfs":        [],
                "bds":         [],
                "contracts":   [],
                "filters":     []
            }
        ],
        "sites": []
    }

    print(f"\n  [PROVISIONING] Création Schema : {schema_name}")
    resp = requests.post(url, headers=get_headers(), json=payload, verify=False, timeout=30)

    if resp.status_code not in [200, 201]:
        raise Exception(f"[ERREUR create_schema] Status {resp.status_code} — {resp.text[:300]}")

    data      = resp.json()
    schema_id = data.get("id")
    print(f"  ✅ Schema '{schema_name}' créé — ID: {schema_id}")
    print(f"     Template '{template_name}' inclus")
    return schema_id


# ── 3. AJOUTER UN VRF AU TEMPLATE ───────────────────────────
def add_vrf_to_template(schema_id, template_name, vrf_name):
    """
    Ajoute un VRF dans un Template MSO via PATCH.
    Dans MSO, les modifications de Template utilisent PATCH avec
    un tableau d'opérations JSON Patch (RFC 6902).
    """
    url = f"{MSO_URL}/api/v1/schemas/{schema_id}"

    # JSON Patch — opération "add" sur le tableau vrfs du Template
    payload = {
        "ops": [
            {
                "op":    "add",
                "path":  f"/templates/{template_name}/vrfs/-",
                "value": {
                    "name":        vrf_name,
                    "displayName": vrf_name,
                    "l3MCast":     False,
                    "preferredGroup": False
                }
            }
        ]
    }

    print(f"\n  [PROVISIONING] Ajout VRF '{vrf_name}' dans Template '{template_name}'")
    resp = requests.patch(url, headers=get_headers(), json=payload, verify=False, timeout=30)

    if resp.status_code not in [200, 201]:
        raise Exception(f"[ERREUR add_vrf] Status {resp.status_code} — {resp.text[:300]}")

    print(f"  VRF '{vrf_name}' ajouté")
    return resp.json()


# ── 4. AJOUTER UN BD AU TEMPLATE ────────────────────────────
def add_bd_to_template(schema_id, template_name, bd_name, vrf_name, subnet="192.168.100.1/24"):
    """
    Ajoute un Bridge Domain dans un Template MSO.
    Le BD est lié au VRF via une référence bdRef.

    DIFFÉRENCE APIC vs MSO :
      APIC : fvBD avec fvRsCtx enfant → POST séparé
      MSO  : bd object avec vrfRef intégré → PATCH sur le schema
    """
    url = f"{MSO_URL}/api/v1/schemas/{schema_id}"

    vrf_ref = f"/schemas/{schema_id}/templates/{template_name}/vrfs/{vrf_name}"

    payload = {
        "ops": [
            {
                "op":    "add",
                "path":  f"/templates/{template_name}/bds/-",
                "value": {
                    "name":        bd_name,
                    "displayName": bd_name,
                    "vrfRef":      vrf_ref,
                    "l2UnknownUnicast":         "proxy",
                    "l2Stretch":                True,
                    "intersiteBumTrafficAllow": True,
                    "subnets": [
                        {
                            "ip":    subnet,
                            "scope": "public",
                            "shared": False
                        }
                    ]
                }
            }
        ]
    }

    print(f"\n  [PROVISIONING] Ajout BD '{bd_name}' → VRF '{vrf_name}'")
    resp = requests.patch(url, headers=get_headers(), json=payload, verify=False, timeout=30)

    if resp.status_code not in [200, 201]:
        raise Exception(f"[ERREUR add_bd] Status {resp.status_code} — {resp.text[:300]}")

    print(f"  BD '{bd_name}' ajouté (subnet: {subnet})")
    return resp.json()


# ── 5. AJOUTER UN ANP + EPG AU TEMPLATE ─────────────────────
def add_anp_epg_to_template(schema_id, template_name, anp_name, epg_name, bd_name):
    """
    Ajoute un Application Profile (ANP) et un EPG dans un Template MSO.
    L'ANP et l'EPG sont créés ensemble dans une seule opération PATCH.

    ANP = Application Network Profile (équivalent fvAp dans APIC)
    EPG = Endpoint Group (équivalent fvAEPg dans APIC)
    """
    url = f"{MSO_URL}/api/v1/schemas/{schema_id}"

    bd_ref  = f"/schemas/{schema_id}/templates/{template_name}/bds/{bd_name}"
    anp_ref = f"/schemas/{schema_id}/templates/{template_name}/anps/{anp_name}"

    payload = {
        "ops": [
            {
                "op":    "add",
                "path":  f"/templates/{template_name}/anps/-",
                "value": {
                    "name":        anp_name,
                    "displayName": anp_name,
                    "epgs": [
                        {
                            "name":        epg_name,
                            "displayName": epg_name,
                            "bdRef":       bd_ref,
                            "anpRef":      anp_ref,
                            "uSegEpg":     False,
                            "intraEpg":    "unenforced",
                            "subnets":     [],
                            "contractRelationships": []
                        }
                    ]
                }
            }
        ]
    }

    print(f"\n  [PROVISIONING] Ajout ANP '{anp_name}' + EPG '{epg_name}'")
    resp = requests.patch(url, headers=get_headers(), json=payload, verify=False, timeout=30)

    if resp.status_code not in [200, 201]:
        raise Exception(f"[ERREUR add_anp_epg] Status {resp.status_code} — {resp.text[:300]}")

    print(f"  ANP '{anp_name}' + EPG '{epg_name}' ajoutés")
    return resp.json()


# ── 6. ASSOCIER LE TEMPLATE À UN SITE ───────────────────────
def associate_template_to_site(schema_id, template_name, site_id):
    """
    Associe un Template à un site ACI.
    Sans cette étape, les objets du Template ne sont pas déployés.

    C'est la grande valeur ajoutée de MSO :
    un seul Template peut être associé à PLUSIEURS sites simultanément.
    """
    url = f"{MSO_URL}/api/v1/schemas/{schema_id}"

    payload = {
        "ops": [
            {
                "op":    "add",
                "path":  "/sites/-",
                "value": {
                    "siteId":   site_id,
                    "templates": [{"name": template_name}]
                }
            }
        ]
    }

    print(f"\n  [PROVISIONING] Association Template '{template_name}' → Site ID '{site_id}'")
    resp = requests.patch(url, headers=get_headers(), json=payload, verify=False, timeout=30)

    if resp.status_code not in [200, 201]:
        raise Exception(f"[ERREUR associate_site] Status {resp.status_code} — {resp.text[:300]}")

    print(f"  Template associé au site")
    return resp.json()


# ── 7. DÉPLOYER LE TEMPLATE ─────────────────────────────────
def deploy_template(schema_id, template_name):
    """
    Déploie le Template sur tous les sites associés.
    C'est cette étape qui pousse la configuration sur les APICs.

    Dans APIC (Tâche 1) : chaque objet est immédiatement actif à la création.
    Dans MSO (Tâche 2)  : les objets sont définis dans le Template, puis
                          déployés en une seule opération sur les sites.
    """
    url     = f"{MSO_URL}/api/v1/schemas/{schema_id}/deploy"
    payload = {"templateName": template_name}

    print(f"\n  [PROVISIONING] Déploiement Template '{template_name}' sur les sites...")
    resp = requests.post(url, headers=get_headers(), json=payload, verify=False, timeout=60)

    if resp.status_code not in [200, 201, 202]:
        raise Exception(f"[ERREUR deploy] Status {resp.status_code} — {resp.text[:300]}")

    print(f"  Template '{template_name}' déployé sur tous les sites associés")
    return resp.json()


# ── 8. SUPPRESSION ──────────────────────────────────────────
def delete_schema(schema_id, schema_name):
    """
    Supprime un Schema MSO et tous ses Templates.
    Cela undeploy aussi la configuration sur les sites.
    """
    url  = f"{MSO_URL}/api/v1/schemas/{schema_id}"
    print(f"\n  [DELETE] Suppression Schema '{schema_name}' (ID: {schema_id})")
    resp = requests.delete(url, headers=get_headers(), verify=False, timeout=30)

    if resp.status_code not in [200, 201, 204]:
        raise Exception(f"[ERREUR delete_schema] Status {resp.status_code} — {resp.text[:300]}")

    print(f"  Schema supprimé")


def delete_tenant(tenant_id, tenant_name):
    """
    Supprime un Tenant MSO.
    Supprimer d'abord tous les Schemas associés au Tenant.
    """
    url  = f"{MSO_URL}/api/v1/tenants/{tenant_id}"
    print(f"\n  [DELETE] Suppression Tenant '{tenant_name}' (ID: {tenant_id})")
    resp = requests.delete(url, headers=get_headers(), verify=False, timeout=30)

    if resp.status_code not in [200, 201, 204]:
        raise Exception(f"[ERREUR delete_tenant] Status {resp.status_code} — {resp.text[:300]}")

    print(f"  Tenant supprimé")


if __name__ == "__main__":
    print("provisioning.py — fonctions MSO prêtes")
    print("Lancer main.py pour le cycle complet")