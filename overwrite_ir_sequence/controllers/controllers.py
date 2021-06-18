# -*- coding: utf-8 -*-
# from odoo import http


# class OverwriteIrSequence(http.Controller):
#     @http.route('/overwrite_ir_sequence/overwrite_ir_sequence/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/overwrite_ir_sequence/overwrite_ir_sequence/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('overwrite_ir_sequence.listing', {
#             'root': '/overwrite_ir_sequence/overwrite_ir_sequence',
#             'objects': http.request.env['overwrite_ir_sequence.overwrite_ir_sequence'].search([]),
#         })

#     @http.route('/overwrite_ir_sequence/overwrite_ir_sequence/objects/<model("overwrite_ir_sequence.overwrite_ir_sequence"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('overwrite_ir_sequence.object', {
#             'object': obj
#         })
