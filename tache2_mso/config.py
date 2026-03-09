# ── Nexus Dashboard / MSO (NDO) ──────────────────────────────
# Remplacer par l'IP réelle quand le sandbox sera disponible
MSO_URL  = "https://<mso-host>"  
USERNAME = "admin"
PASSWORD = "Cisco.12345!"

# ── Domaine de login ─────────────────────────────────────────
LOGIN_DOMAIN = "local"            # ou "DefaultAuth"

# ── Fabric / Site cible ──────────────────────────────────────
SITE_NAME    = "StagePFE_Site"    # nom du site ACI cible

# ── Objets à créer ───────────────────────────────────────────
TENANT_NAME   = "StagePFE_MSO"
SCHEMA_NAME   = "StagePFE_Schema"
TEMPLATE_NAME = "StagePFE_Template"
VRF_NAME      = "VRF_PROD"
BD_NAME       = "BD_WEB"
ANP_NAME      = "AP_WEB"
EPG_NAME      = "EPG_FRONTEND"