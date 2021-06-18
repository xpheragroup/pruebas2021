# -*- coding: utf-8 -*-
# from odoo import http


# class Tracking-fields(http.Controller):
#     @http.route('/tracking-fields/tracking-fields/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tracking-fields/tracking-fields/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tracking-fields.listing', {
#             'root': '/tracking-fields/tracking-fields',
#             'objects': http.request.env['tracking-fields.tracking-fields'].search([]),
#         })

#     @http.route('/tracking-fields/tracking-fields/objects/<model("tracking-fields.tracking-fields"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tracking-fields.object', {
#             'object': obj
#         })
