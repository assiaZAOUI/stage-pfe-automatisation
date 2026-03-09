Cycle complet en 5 étapes :
#   1. Authentification  → token JWT (Cookie: AuthCookie)
#   2. Collecte AVANT    → Sites, Tenants, Schemas → JSON
#   3. Provisioning      → Tenant → Schema → VRF → BD → ANP → EPG → Deploy
#   4. Vérification      → Collecte APRÈS → JSON
#   5. Nettoyage         → Delete Schema → Delete Tenant
# ============================================================

import json
from auth       import test_auth, get_token
from collector  import export_inventory, get_sites, get_tenants, get_schemas
from provisioning import (create_tenant, create_schema,
                           add_vrf_to_template, add_bd_to_template,
                           add_anp_epg_to_template, associate_template_to_site,
                           deploy_template, delete_schema, delete_tenant)
from config import (TENANT_NAME, SCHEMA_NAME, TEMPLATE_NAME,
                    VRF_NAME, BD_NAME, ANP_NAME, EPG_NAME)


def separator(title):
    print(f"\n{'='*60}")
    print(f"  ÉTAPE : {title}")
    print(f"{'='*60}")


def main():
    print("\n" + "="*60)
    print("  TÂCHE 2 — CISCO MSO/NDO REST API")
    print("  Stagiaire : Assia Zaoui")
    print("="*60)

    # ──────────────────────────────────────────────────────────
    # ÉTAPE 1 — AUTHENTIFICATION
    # ──────────────────────────────────────────────────────────
    separator("1 — AUTHENTIFICATION MSO/NDO")
    ok = test_auth()
    if not ok:
        print("\n  Authentification échouée — arrêt du script")
        return

    # ──────────────────────────────────────────────────────────
    # ÉTAPE 2 — COLLECTE AVANT PROVISIONING
    # ──────────────────────────────────────────────────────────
    separator("2 — COLLECTE AVANT PROVISIONING")
    inventaire_avant = export_inventory("inventaire_mso_avant.json")

    nb_tenants_avant = len(inventaire_avant.get("tenants", []))
    nb_schemas_avant = len(inventaire_avant.get("schemas", []))
    nb_sites_avant   = len(inventaire_avant.get("sites",   []))
    print(f"\n  Résumé AVANT :")
    print(f"    Sites   : {nb_sites_avant}")
    print(f"    Tenants : {nb_tenants_avant}")
    print(f"    Schemas : {nb_schemas_avant}")

    # Récupérer l'ID du premier site disponible pour l'association
    sites = inventaire_avant.get("sites", [])
    site_id = sites[0]["id"] if sites else None
    if site_id:
        print(f"    Site cible : {sites[0].get('name','?')} (ID: {site_id})")
    else:
        print(f"     Aucun site disponible — deploy ignoré")

    # ──────────────────────────────────────────────────────────
    # ÉTAPE 3 — PROVISIONING
    # ──────────────────────────────────────────────────────────
    separator("3 — PROVISIONING MSO/NDO")

    # 3.1 — Créer le Tenant
    print("\n  3.1 — Tenant")
    tenant_id = create_tenant(TENANT_NAME, "Stage PFE — Automatisation MSO REST API")

    # 3.2 — Créer le Schema + Template
    print("\n  3.2 — Schema + Template")
    schema_id = create_schema(SCHEMA_NAME, TEMPLATE_NAME, tenant_id)

    # 3.3 — Ajouter le VRF au Template
    print("\n  3.3 — VRF")
    add_vrf_to_template(schema_id, TEMPLATE_NAME, VRF_NAME)

    # 3.4 — Ajouter le BD au Template (lié au VRF)
    print("\n  3.4 — Bridge Domain")
    add_bd_to_template(schema_id, TEMPLATE_NAME, BD_NAME, VRF_NAME,
                       subnet="192.168.100.1/24")

    # 3.5 — Ajouter ANP + EPG au Template (lié au BD)
    print("\n  3.5 — ANP + EPG")
    add_anp_epg_to_template(schema_id, TEMPLATE_NAME, ANP_NAME, EPG_NAME, BD_NAME)

    # 3.6 — Associer le Template au site (si disponible)
    if site_id:
        print("\n  3.6 — Association Template → Site")
        associate_template_to_site(schema_id, TEMPLATE_NAME, site_id)

        # 3.7 — Déployer le Template sur le site
        print("\n  3.7 — Déploiement")
        deploy_template(schema_id, TEMPLATE_NAME)
    else:
        print("\n  3.6 — Pas de site disponible → deploy ignoré")

    print(f"\n  Provisioning complet :")
    print(f"     Tenant   : {TENANT_NAME}   (ID: {tenant_id})")
    print(f"     Schema   : {SCHEMA_NAME}   (ID: {schema_id})")
    print(f"     Template : {TEMPLATE_NAME}")
    print(f"     VRF      : {VRF_NAME}")
    print(f"     BD       : {BD_NAME}")
    print(f"     ANP      : {ANP_NAME}")
    print(f"     EPG      : {EPG_NAME}")

    # ──────────────────────────────────────────────────────────
    # ÉTAPE 4 — VÉRIFICATION APRÈS PROVISIONING
    # ──────────────────────────────────────────────────────────
    separator("4 — VÉRIFICATION APRÈS PROVISIONING")
    inventaire_apres = export_inventory("inventaire_mso_apres.json")

    nb_tenants_apres = len(inventaire_apres.get("tenants", []))
    nb_schemas_apres = len(inventaire_apres.get("schemas", []))

    print(f"\n  Comparaison AVANT / APRÈS :")
    print(f"    Tenants : {nb_tenants_avant} → {nb_tenants_apres}  (+{nb_tenants_apres - nb_tenants_avant})")
    print(f"    Schemas : {nb_schemas_avant} → {nb_schemas_apres}  (+{nb_schemas_apres - nb_schemas_avant})")

    # Vérifier que notre tenant est bien présent
    tenants_apres = inventaire_apres.get("tenants", [])
    notre_tenant  = next((t for t in tenants_apres if t.get("name") == TENANT_NAME), None)
    if notre_tenant:
        print(f"\n  Tenant '{TENANT_NAME}' confirmé dans MSO (ID: {notre_tenant.get('id')})")
    else:
        print(f"\n  Tenant '{TENANT_NAME}' non trouvé dans la liste")

    # ──────────────────────────────────────────────────────────
    # ÉTAPE 5 — NETTOYAGE
    # ──────────────────────────────────────────────────────────
    separator("5 — NETTOYAGE")
    print("  Suppression du Schema puis du Tenant...")

    # Supprimer d'abord le Schema (undeploy + suppression des Templates)
    delete_schema(schema_id, SCHEMA_NAME)

    # Supprimer ensuite le Tenant
    delete_tenant(tenant_id, TENANT_NAME)

    print(f"\n  Nettoyage complet")

    # ──────────────────────────────────────────────────────────
    # RÉSUMÉ FINAL
    # ──────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  RÉSUMÉ FINAL — TÂCHE 2 MSO/NDO")
    print(f"{'='*60}")
    print(f"  Étape 1 — Authentification JWT (Cookie: AuthCookie)")
    print(f"  Étape 2 — Collecte : {nb_sites_avant} sites, {nb_tenants_avant} tenants, {nb_schemas_avant} schemas")
    print(f"  Étape 3 — Provisioning : {TENANT_NAME} / {SCHEMA_NAME} / {VRF_NAME} / {BD_NAME} / {EPG_NAME}")
    print(f"  Étape 4 — Vérification : {nb_tenants_avant} → {nb_tenants_apres} tenants")
    print(f"  Étape 5 — Nettoyage complet")
    print(f"\n  Fichiers générés :")
    print(f"    → inventaire_mso_avant.json")
    print(f"    → inventaire_mso_apres.json")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()