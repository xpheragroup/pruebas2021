# -*- coding: utf-8 -*-
# from odoo import http


# class ExternalRequisitions(http.Controller):
#     @http.route('/external_requisitions/external_requisitions/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/external_requisitions/external_requisitions/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('external_requisitions.listing', {
#             'root': '/external_requisitions/external_requisitions',
#             'objects': http.request.env['external_requisitions.external_requisitions'].search([]),
#         })

#     @http.route('/external_requisitions/external_requisitions/objects/<model("external_requisitions.external_requisitions"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('external_requisitions.object', {
#             'object': obj
#         })
