import datetime

from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    city_id = fields.Char(string='Ciudad')
    department_id = fields.Many2one("res.country.state", string='Departamento', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    region_id = fields.Selection([
        ('amazonia','Amazonia'),
        ('andina','Andina'),
        ('caribe','Caribe'),
        ('insular','Insular'),
        ('orinoquía','Orinoquía'),
        ('pacífico','Pacífico')
        ], string='Región')
    country_id = fields.Many2one('res.country', string='País')
    partner_id = fields.Many2one('res.partner', string='Customer', auto_join=True, tracking=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    _sql_constraints = [
        (
            "unique_partner",
            "UNIQUE (partner_id)",
            "Ya existe un centro de costos para este cliente.",
        )
    ]


