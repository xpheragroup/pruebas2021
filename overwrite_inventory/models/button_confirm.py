from odoo import models, fields


class button_confirm(models.TransientModel):
    _name = "overwrite_inventory.button.confirm"

    def button_confirm(self):
        query = [['id', '=', self._context['scrap']]]
        stock_scrap = self.env['stock.scrap'].search(query)
        stock_scrap.action_validate_second_confirm()
        return {
            'type': 'ir.actions.act_window_close'
        }


class ButtonConfirmGeneric(models.TransientModel):
    _name = "overwrite_inventory.button.confirm.generic"

    message = fields.Char(readonly=True)

    def button_confirm(self):
        query = [['id', '=', self._context['id']]]
        row = self.env[self._context['model']].search(query)
        row.button_validate_confirm()
        return {
            'type': 'ir.actions.act_window_close'
        }
