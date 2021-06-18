# -*- coding: utf-8 -*-
# from odoo import http


# class OverwriteProduct(http.Controller):
#     @http.route('/overwrite_product/overwrite_product/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/overwrite_product/overwrite_product/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('overwrite_product.listing', {
#             'root': '/overwrite_product/overwrite_product',
#             'objects': http.request.env['overwrite_product.overwrite_product'].search([]),
#         })

#     @http.route('/overwrite_product/overwrite_product/objects/<model("overwrite_product.overwrite_product"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('overwrite_product.object', {
#             'object': obj
#         })
