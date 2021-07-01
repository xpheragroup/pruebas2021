# -*- coding: utf-8 -*-
# from odoo import http


# class OverwriteAccountMove(http.Controller):
#     @http.route('/overwrite_account_move/overwrite_account_move/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/overwrite_account_move/overwrite_account_move/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('overwrite_account_move.listing', {
#             'root': '/overwrite_account_move/overwrite_account_move',
#             'objects': http.request.env['overwrite_account_move.overwrite_account_move'].search([]),
#         })

#     @http.route('/overwrite_account_move/overwrite_account_move/objects/<model("overwrite_account_move.overwrite_account_move"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('overwrite_account_move.object', {
#             'object': obj
#         })
