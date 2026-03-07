# ─────────────────────────────────────────────────────────────
#  TÂCHE 1 (ancienne) — Nexus Dashboard NDFC
# ─────────────────────────────────────────────────────────────

# from auth import get_token
# from collector import get_fabrics, get_switches, get_vrfs, get_networks, export_inventory_to_json
# from provisioning import create_vrf, create_network, delete_vrf, delete_network
#
# FABRIC = "DevNet_VxLAN_Fabric"
#
# if __name__ == "__main__":
#
#     # Étape 1 — Auth
#     token = get_token()
#
#     # Étape 2 — Collecte
#     get_fabrics()
#     get_switches(FABRIC)
#     get_vrfs(FABRIC)
#     get_networks(FABRIC)
#     export_inventory_to_json(FABRIC, "inventaire_avant.json")
#
#     # Étape 3 — Provisioning
#     create_vrf(FABRIC, "StagePFE_VRF", vrf_id=50099, vlan_id=3099)
#     create_network(FABRIC, "StagePFE_Network", vlan_id=2099,
#                    vrf_name="StagePFE_VRF", gateway_ip="192.168.99.1/24")
#
#     # Étape 4 — Vérification
#     get_vrfs(FABRIC)
#     get_networks(FABRIC)
#     export_inventory_to_json(FABRIC, "inventaire_apres.json")
#
#     # Étape 5 — Nettoyage (ordre obligatoire : Network avant VRF)
#     input("\nAppuie sur Entrée pour supprimer...")
#     delete_network(FABRIC, "StagePFE_Network")
#     delete_vrf(FABRIC, "StagePFE_VRF")

# ─────────────────────────────────────────────────────────────
#  TÂCHE 1 (nouvelle) — Cisco APIC
# ─────────────────────────────────────────────────────────────

from auth import get_token
from collector import (get_tenants, get_vrfs, get_bridge_domains,
                       get_epgs, get_nodes, export_inventory)
from provisioning import (create_tenant, create_vrf, create_bridge_domain,
                          create_ap, create_epg, delete_tenant)

if __name__ == "__main__":

    # ── ÉTAPE 1 — AUTHENTIFICATION ────────────────────────────
    print("\n" + "="*50)
    print("  ÉTAPE 1 — AUTHENTIFICATION APIC")
    print("="*50)
    token = get_token()
    if not token:
        print("Authentification échouée — arrêt du script")
        exit()

    # ── ÉTAPE 2 — COLLECTE (état initial) ─────────────────────
    print("\n" + "="*50)
    print("  ÉTAPE 2 — COLLECTE (état initial)")
    print("="*50)
    get_tenants()
    get_vrfs()
    get_bridge_domains()
    get_epgs()
    get_nodes()
    export_inventory("inventaire_apic_avant.json")

    # ── ÉTAPE 3 — PROVISIONING ────────────────────────────────
    print("\n" + "="*50)
    print("  ÉTAPE 3 — PROVISIONING")
    print("="*50)

    # Ordre obligatoire : Tenant → VRF → BD → AP → EPG
    create_tenant("StagePFE",        "Tenant créé en stage PFE — Assia Zaoui")
    create_vrf("StagePFE",           "VRF_PROD")
    create_bridge_domain("StagePFE", "BD_WEB",      "VRF_PROD")
    create_ap("StagePFE",            "AP_WEB")
    create_epg("StagePFE",           "AP_WEB",      "EPG_FRONTEND", "BD_WEB")

    # ── ÉTAPE 4 — VÉRIFICATION ────────────────────────────────
    print("\n" + "="*50)
    print("  ÉTAPE 4 — VÉRIFICATION")
    print("="*50)
    get_tenants()
    get_vrfs()
    get_bridge_domains()
    get_epgs()
    export_inventory("inventaire_apic_apres.json")

    # ── ÉTAPE 5 — NETTOYAGE ───────────────────────────────────
    print("\n" + "="*50)
    print("  ÉTAPE 5 — NETTOYAGE")
    print("="*50)
    input("\nAppuie sur Entrée pour supprimer les objets de test...")

    # Supprimer le Tenant supprime automatiquement :
    # AP_WEB → EPG_FRONTEND → BD_WEB → VRF_PROD
    delete_tenant("StagePFE")

    print("\n Script APIC terminé avec succès !")