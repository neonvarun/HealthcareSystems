from plugs.manager import PlugManager
from plugs.plug import Plug

plugs = [
    # Odoo ERP Integration Plugin
    # Syncs invoices, payments, patients, inventory to/from Odoo ERP
    # Configure via CARE_ODOO_* environment variables
    # Odoo instance expected at the host/port configured below
    Plug(
        name="care_odoo",
        package_name="care_odoo",
        version="0.1.0",
        configs={
            "CARE_ODOO_HOST": "odoo",
            "CARE_ODOO_PORT": "8069",
            "CARE_ODOO_PROTOCOL": "http",
            "CARE_ODOO_DATABASE": "care",
            "CARE_ODOO_USERNAME": "admin",
            "CARE_ODOO_PASSWORD": "admin",
        },
    ),
]

manager = PlugManager(plugs)
