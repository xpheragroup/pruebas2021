# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    warehouse_id = fields.Many2one('stock.warehouse',string='Almacen')
