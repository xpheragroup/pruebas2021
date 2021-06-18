# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import io
import logging
import os
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
from odoo.modules.module import get_resource_path

from random import randrange
from PIL import Image

_logger = logging.getLogger(__name__)

class Company(models.Model):
    _name = "res.company"
    _inherit = "res.company"

    empresa_copy_ldm = fields.Many2one('res.company', string='Compañía copia LdM', index=True,
                    readonly=True, states={'no_copy': [('readonly', False)]},)

    copy_ldm = fields.Many2many(string="Listas de materiales asociadas a Compañía copia LdM",
                    comodel_name='mrp.bom',
                    relation="bom_company_copy",
                    help="Selección de Listas de materiales asociadas a Compañía copia LdM.",
                    domain="[('company_id','=',empresa_copy_ldm)]",
                    #required=True,
                    readonly=True, states={'no_copy': [('readonly', False)]},)

    # Sistema de Estados
    state = fields.Selection([
        ('no_copy', 'LdM No copiada.'),
        ('copied', 'Ldm Copiada.')], string='Estado',
        copy=False, index=True, readonly=True,
        store=True, tracking=True, default='no_copy',
        help=" * LdM No copiada: La lista de materiales no se ha copiado.\n"
             " * LdM Copiada: La lista de materiales se ha copiado de la Compañía copia LdM seleccionada.")

    def action_copy_ldm(self):
        self.state = 'copied'
        _logger.critical("LdM Copiada.")

        if self.copy_ldm:
            # warehouse = self.warehouse_id #and self.warehouse_id.company_id.id == self.id and self.warehouse_id or False
            # picking_type_id = self.env['stock.picking.type'].search([
            #                         ('warehouse_id', '=', warehouse.id), 
            #                         ('company_id', '=', self.id)], limit=1)
            BomLine = self.env['mrp.bom.line']

            for ldm in self.copy_ldm:
                # Create BOM
                bom_created = self.env['mrp.bom'].create({
                    'company_id': self.id,
                    #'picking_type_id': picking_type_id.id,
                    'product_tmpl_id': ldm.product_tmpl_id.id,
                    'product_id': ldm.product_id.id,
                    'product_qty': 1.0,
                    'type': 'normal',
                    #'bom_line_ids': [(6, 0, [p.id for p in ldm.bom_line_ids])],
                    #'bom_line_ids': [(4, p.id) for p in ldm.bom_line_ids],
                })

                for linea_bom in ldm.bom_line_ids:
                    linea_bom_copy = linea_bom.copy()
                    linea_bom_copy.company_id = self.id
                    linea_bom_copy.bom_id = bom_created.id


                # for linea_bom in ldm.bom_line_ids:
                #     BomLine.create({
                #         'company_id': self.id,
                #         'bom_id': bom_created.id,
                #         'product_id': linea_bom.product_tmpl_id.product_variant_id.id,
                #         'product_qty_display': linea_bom.product_qty_display,
                #         'product_uom_id_display': linea_bom.product_uom_id_display.id,
                #         'product_uom_id': linea_bom.product_uom_id.id,
                #         #'product_uom_id': linea_bom.product_id.uom_id.id,
                #     })
                
        else:
            raise UserError(_("No se encuentra ninguna lista de materiales asociada a la companía seleccionada."))



        return True


    @api.onchange('empresa_copy_ldm')
    def _onchange_empresa_copy_ldm(self):
        self.copy_ldm = None

        if self.empresa_copy_ldm:
            self.copy_ldm = self.env['mrp.bom'].search([('company_id', '=', self.empresa_copy_ldm.id)])
            _logger.critical("self.copy_ldm")
            _logger.critical(self.copy_ldm)
