# -*- coding: utf-8 -*-
# from odoo import http


# class TrackingViewFix(http.Controller):
#     @http.route('/tracking_view_fix/tracking_view_fix/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tracking_view_fix/tracking_view_fix/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tracking_view_fix.listing', {
#             'root': '/tracking_view_fix/tracking_view_fix',
#             'objects': http.request.env['tracking_view_fix.tracking_view_fix'].search([]),
#         })

#     @http.route('/tracking_view_fix/tracking_view_fix/objects/<model("tracking_view_fix.tracking_view_fix"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tracking_view_fix.object', {
#             'object': obj
#         })
