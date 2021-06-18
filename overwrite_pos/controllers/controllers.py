# -*- coding: utf-8 -*-
# from odoo import http


# class OverwritePos(http.Controller):
#     @http.route('/overwrite_pos/overwrite_pos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/overwrite_pos/overwrite_pos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('overwrite_pos.listing', {
#             'root': '/overwrite_pos/overwrite_pos',
#             'objects': http.request.env['overwrite_pos.overwrite_pos'].search([]),
#         })

#     @http.route('/overwrite_pos/overwrite_pos/objects/<model("overwrite_pos.overwrite_pos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('overwrite_pos.object', {
#             'object': obj
#         })
