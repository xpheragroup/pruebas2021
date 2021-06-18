# -*- coding: utf-8 -*-
# from odoo import http


# class OverwriteProduction(http.Controller):
#     @http.route('/overwrite_production/overwrite_production/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/overwrite_production/overwrite_production/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('overwrite_production.listing', {
#             'root': '/overwrite_production/overwrite_production',
#             'objects': http.request.env['overwrite_production.overwrite_production'].search([]),
#         })

#     @http.route('/overwrite_production/overwrite_production/objects/<model("overwrite_production.overwrite_production"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('overwrite_production.object', {
#             'object': obj
#         })
