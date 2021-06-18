# -*- coding: utf-8 -*-
# from odoo import http


# class ModuloXphera(http.Controller):
#     @http.route('/modulo_xphera/modulo_xphera/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/modulo_xphera/modulo_xphera/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('modulo_xphera.listing', {
#             'root': '/modulo_xphera/modulo_xphera',
#             'objects': http.request.env['modulo_xphera.modulo_xphera'].search([]),
#         })

#     @http.route('/modulo_xphera/modulo_xphera/objects/<model("modulo_xphera.modulo_xphera"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('modulo_xphera.object', {
#             'object': obj
#         })
