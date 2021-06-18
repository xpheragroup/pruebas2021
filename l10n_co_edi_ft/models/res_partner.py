# coding: utf-8
from odoo import api, fields, models, _\



class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_vat_without_verification_code(self):
        self.ensure_one()
        # last digit is the verification code
        return self.vat.split('-')[0] if self.vat else ''

    def _get_vat_verification_code(self):
        self.ensure_one()
        if self.vat:
            if self.vat.isdigit() and len(self.vat) < 16:
                vpri = [0, 3, 7, 13, 17, 19, 23, 29,
                        37, 41, 43, 47, 53, 59, 67, 71]
                x = 0
                y = 0
                for i in range(0, len(self.vat)):
                    y = int(self.vat[i])
                    x = x + (y * vpri[len(self.vat)-i])
                    y = x % 11
                return 11 - y if y > 1 else y
        return ''
