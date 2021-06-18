# -*- coding: utf-8 -*-
import datetime
from odoo import models


class PurchaseOrder(models.Model):
    # Inherit Purchase Requisition
    _inherit = 'purchase.order'

    # Redefininf copy funcion
    def copy(self, default=None):
        default = dict(default or {})
        current_user = self._uid
        far_future_date = datetime.datetime(year=2220, month=1, day=1)
        default.update({
            'user_id': current_user,
            'date_planned': far_future_date
        })
        return super(PurchaseOrder, self).copy(default)
