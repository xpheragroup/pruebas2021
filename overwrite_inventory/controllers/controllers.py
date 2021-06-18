# -*- coding: utf-8 -*-
# from odoo import http


# class OverwriteInventory(http.Controller):
#     @http.route('/overwrite_inventory/overwrite_inventory/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/overwrite_inventory/overwrite_inventory/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('overwrite_inventory.listing', {
#             'root': '/overwrite_inventory/overwrite_inventory',
#             'objects': http.request.env['overwrite_inventory.overwrite_inventory'].search([]),
#         })

#     @http.route('/overwrite_inventory/overwrite_inventory/objects/<model("overwrite_inventory.overwrite_inventory"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('overwrite_inventory.object', {
#             'object': obj
#         })
