from auth import get_token
from collector import get_fabrics, get_switches, get_vrfs, get_networks, export_inventory_to_json
from provisioning import create_vrf, create_network, delete_network, delete_vrf

FABRIC = "DevNet_VxLAN_Fabric"

if __name__ == "__main__":

    print("\n" + "="*50)
    print("  ÉTAPE 1 — AUTHENTIFICATION")
    print("="*50)
    token = get_token()
    if not token:
        print("Impossible de continuer sans token.")
        exit()

    print("\n" + "="*50)
    print("  ÉTAPE 2 — COLLECTE")
    print("="*50)
    get_fabrics()
    get_switches(FABRIC)
    get_vrfs(FABRIC)
    get_networks(FABRIC)
    export_inventory_to_json(FABRIC, "inventaire_avant.json")

    print("\n" + "="*50)
    print("  ÉTAPE 3 — PROVISIONING")
    print("="*50)
    create_vrf(FABRIC, "StagePFE_VRF", vrf_id=50099, vlan_id=3099)
    create_network(FABRIC, "StagePFE_Network", vlan_id=2099,
                   vrf_name="StagePFE_VRF", gateway_ip="192.168.99.1/24")

    print("\n" + "="*50)
    print("  ÉTAPE 4 — VÉRIFICATION")
    print("="*50)
    get_vrfs(FABRIC)
    get_networks(FABRIC)
    export_inventory_to_json(FABRIC, "inventaire_apres.json")

    print("\n" + "="*50)
    print("  ÉTAPE 5 — NETTOYAGE")
    print("="*50)
    input("\nAppuie sur Entrée pour supprimer les objets de test...")
    delete_network(FABRIC, "StagePFE_Network")
    delete_vrf(FABRIC, "StagePFE_VRF")

    print("\n Script terminé !")
