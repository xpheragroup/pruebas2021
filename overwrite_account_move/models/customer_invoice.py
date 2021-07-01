from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
from odoo.tools.misc import formatLang, format_date, get_lang

from collections import defaultdict
from datetime import date, timedelta
from itertools import groupby
from itertools import zip_longest
from hashlib import sha256
from json import dumps

import json
import re

class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_line_ids = fields.One2many('account.move.line', 'move_id', string='Invoice lines',
        copy=False, readonly=True,
        domain=[('exclude_from_invoice_tab', '=', False)],
        states={'draft': [('readonly', False)]})

    consolidar = fields.Boolean("Consolidar Ordenes de Entrega", default=False, copy=False)
    consolidar_ordenes_entrega = fields.Many2many('stock.picking', string='Órdenes de Entrega', copy=False)
    
    @api.onchange('consolidar_ordenes_entrega')
    def consol_ordenes_entrega(self):

        self.invoice_line_ids=None

        list_order_lines=[[]]
        consolidate_cuantity=0
        for order_line in self.consolidar_ordenes_entrega._origin:

            for product_line in order_line.move_line_ids_without_package._origin:
                exist=False
                for consol_line in list_order_lines:
                    
                    if consol_line:
                        if (consol_line[0] == product_line.product_id.id) and (consol_line[2] == product_line.product_uom_id):
                            consol_line[1] += product_line.qty_done
                            exist=True

                if not exist:
                    list_order_lines[consolidate_cuantity].append(product_line.product_id.id)
                    list_order_lines[consolidate_cuantity].append(product_line.qty_done)
                    list_order_lines[consolidate_cuantity].append(product_line.product_uom_id)
                    list_order_lines[consolidate_cuantity].append(product_line.product_id.list_price)
                    list_order_lines.append([])
                    vals_list={}
                    self.invoice_line_ids += self.env['account.move.line'].new(vals_list)
                    consolidate_cuantity += 1
            
        position=0
        list_order_lines.pop()
        for line_consol in self.invoice_line_ids:
            line_consol.product_id=list_order_lines[position][0]
            line_consol.quantity=list_order_lines[position][1]
            line_consol.product_uom_id=list_order_lines[position][2]
            line_consol.price_unit=list_order_lines[position][3]
            position+=1

class Picking(models.Model):

    _inherit = "stock.picking"

    consolidar_invoice = fields.Boolean("Orden de entrega consolidada", default=False, help='Se marca verdadero si ya ha sido involucada en una factura.')
    consolidar_invoice_ref = fields.Char("Códigos de factura", default=False, help='Se registra el código de la factura en la que fue consolidad.')
