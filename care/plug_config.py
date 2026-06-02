from plugs.manager import PlugManager
from plugs.plug import Plug

odoo_plug = Plug(
	name="care_odoo",
	package_name="git+https://github.com/ohcnetwork/care_odoo_be.git",
	version="@main",
	configs={
		"CARE_ODOO_HOST": "odoo",
		"CARE_ODOO_PORT": "8069",
		"CARE_ODOO_PROTOCOL": "http",
		"CARE_ODOO_DATABASE": "care_odoo",
		"CARE_ODOO_USERNAME": "admin",
		"CARE_ODOO_PASSWORD": "admin",
	},
)

plugs = [odoo_plug]

manager = PlugManager(plugs)
