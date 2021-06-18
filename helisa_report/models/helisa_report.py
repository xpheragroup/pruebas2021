# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HelisaReport(models.TransientModel):
    _name = "helisa"

    filename = fields.Char()

    def helisa_report(self):
        active_ids = self._context.get('active_ids', [])
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/helisa_report?ids=%s&filename=%s' % (active_ids, self.filename if self.filename else ''),
            'target': 'new',
        }
