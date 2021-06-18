
from datetime import datetime
from uuid import uuid4
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class PosConfig(models.Model):
    _inherit = 'pos.config'

    numeracion_facturacion = fields.Char("Autorización Facturación")
    range0 = fields.Char("Inicio rango autorizado")
    range1 = fields.Char("Fin rango autorizado")
    fact_code = fields.Char("Código consecutivo de factura")