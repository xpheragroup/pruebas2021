# -*- coding: utf-8 -*-
import datetime
from odoo import models


class PurchaseRequisition(models.Model):
    # Inherit purchase requisition
    _inherit = 'purchase.requisition'

    def copy(self, default=None):                           # Redefininf copy funcion
        default = dict(default or {})
        current_user = self._uid
        default.update({
            'user_id': current_user,
        })
        return super(PurchaseRequisition, self).copy(default)
