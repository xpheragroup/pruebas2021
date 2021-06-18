# -*- coding: utf-8 -*-
# from odoo import http


# class InternalRequisitions(http.Controller):
#     @http.route('/internal_requisitions/internal_requisitions/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/internal_requisitions/internal_requisitions/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('internal_requisitions.listing', {
#             'root': '/internal_requisitions/internal_requisitions',
#             'objects': http.request.env['internal_requisitions.internal_requisitions'].search([]),
#         })

#     @http.route('/internal_requisitions/internal_requisitions/objects/<model("internal_requisitions.internal_requisitions"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('internal_requisitions.object', {
#             'object': obj
#         })
