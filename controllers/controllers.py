# -*- coding: utf-8 -*-
from odoo import http

# class VitCreateXenditInvoice(http.Controller):
#     @http.route('/vit_create_xendit_invoice/vit_create_xendit_invoice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vit_create_xendit_invoice/vit_create_xendit_invoice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vit_create_xendit_invoice.listing', {
#             'root': '/vit_create_xendit_invoice/vit_create_xendit_invoice',
#             'objects': http.request.env['vit_create_xendit_invoice.vit_create_xendit_invoice'].search([]),
#         })

#     @http.route('/vit_create_xendit_invoice/vit_create_xendit_invoice/objects/<model("vit_create_xendit_invoice.vit_create_xendit_invoice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vit_create_xendit_invoice.object', {
#             'object': obj
#         })