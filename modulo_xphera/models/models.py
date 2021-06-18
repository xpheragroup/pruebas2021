# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import UserError

# class my_module(models.Model):
#     _name = 'my_module.my_module'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#
#     @api.onchange('product_uom', 'product_uom_qty')
#     def product_uom_change(self):
#         super(SaleOrderLine, self).product_uom_change()
#         res = {}
#         if self.product_uom_qty and self.product_uom_qty > 1:
#             warning = {
#                 'title': "Error validación en el producto {}".format(
#                     self.product_id.name
#                 ),
#                 'message': "Supera la cantidad máxima de (1)",
#                 'type': 'notification',
#             }
#             res.update({'warning': warning})
#         return res

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('date_order')
    def date_order_change(self):
        res = {}
        if self.date_order and self.date_order.replace(second=0, microsecond=0) < datetime.today()\
                .replace(second=0, microsecond=0):
            warning = {
                'title': "Error validación en la fecha: {}".format(
                    self.date_order
                ),
                'message': "Fecha Pedido no puede ser menor a la fecha actual: {}".format(
                    datetime.today()
                ),
                #'type': 'notification',
            }
            self.date_order = datetime.today()
            res.update({'warning': warning})
        return res

# class StockReturnPicking(models.TransientModel):
#     _inherit = "stock.return.picking"
#
#     @api.onchange('quantity')
#     def quantity_change(self):
#         res = {}
#         titulo = ""
#         mensaje = ""
#
#         if self.quantity and self.quantity > self.product_id.qty_available:
#             titulo += "Error validación en la cantidad {}".format(self.quantity)
#             mensaje += "La cantidad a devolver no puede ser mayor a la cantidad en mano. Actual: ".format(self.product_id.qty_available)
#         # if self.quantity and self.quantity >
#         if titulo.length > 1:
#             warning = {
#                 'title': titulo,
#                 'message': mensaje,
#                 #'type': 'notification',
#             }
#             res.update({'warning': warning})
#         return res


class ReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"
    @api.onchange('quantity')
    def quantity_change(self):
        res = {}
        mensaje = ""

        if self.quantity < 0:
            raise UserError(_('La cantidad no puede ser negativa.'))

        if self.quantity and self.quantity > self.product_id.qty_available:
            mensaje += "La cantidad a devolver no puede ser mayor a la cantidad A Mano (Inventario). Actual: {}".format(
                self.product_id.qty_available
            )

        if self.quantity and self.quantity > self.move_id.quantity_done:
            mensaje += "\nLa cantidad a devolver no puede ser mayor a la cantidad Terminado. Actual: {}".format(
                self.move_id.quantity_done
            )

        if len(mensaje) > 1:
            warning = {
                'title': "Error validación en la cantidad: {}".format(self.quantity),
                'message': mensaje,
                #'type': 'notification',
            }
            self.quantity = 0
            res.update({'warning': warning})
        return res

# class ReturnPicking(models.TransientModel):
#     _inherit = 'stock.return.picking'
#
#     @api.onchange('picking_id')
#     def _onchange_picking_id(self):
#         super(ReturnPicking, self)._onchange_picking_id()
#