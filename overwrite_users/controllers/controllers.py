# -*- coding: utf-8 -*-
# from odoo import http


# class OverwriteUsers(http.Controller):
#     @http.route('/overwrite_users/overwrite_users/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/overwrite_users/overwrite_users/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('overwrite_users.listing', {
#             'root': '/overwrite_users/overwrite_users',
#             'objects': http.request.env['overwrite_users.overwrite_users'].search([]),
#         })

#     @http.route('/overwrite_users/overwrite_users/objects/<model("overwrite_users.overwrite_users"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('overwrite_users.object', {
#             'object': obj
#         })
