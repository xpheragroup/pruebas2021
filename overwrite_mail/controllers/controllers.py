# -*- coding: utf-8 -*-
# from odoo import http


# class OverwriteMail(http.Controller):
#     @http.route('/overwrite_mail/overwrite_mail/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/overwrite_mail/overwrite_mail/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('overwrite_mail.listing', {
#             'root': '/overwrite_mail/overwrite_mail',
#             'objects': http.request.env['overwrite_mail.overwrite_mail'].search([]),
#         })

#     @http.route('/overwrite_mail/overwrite_mail/objects/<model("overwrite_mail.overwrite_mail"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('overwrite_mail.object', {
#             'object': obj
#         })
