from odoo import http
from odoo.http import request

from ..authentication.authenticate_user import UserAuthentication


class HealthController(http.Controller):
    @http.route("/api/health", type="http", auth="public", methods=["GET"], csrf=False)
    def health(self, **kwargs):
        try:
            auth_header = request.httprequest.headers.get("Authorization")
            UserAuthentication.get_authenticated_user(auth_header)

            return request.make_json_response(
                {"success": True, "message": "Odoo connector healthy"},
                status=200,
            )
        except ValueError as exc:
            return request.make_json_response(
                {"success": False, "error_type": "ValueError", "message": str(exc)},
                status=400,
            )
        except Exception as exc:
            return request.make_json_response(
                {"success": False, "error_type": "ServerError", "message": str(exc)},
                status=500,
            )