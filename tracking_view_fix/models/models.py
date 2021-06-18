from odoo import api, models, _
from odoo.tools import config
from odoo.tools import format_datetime



class MrpStockReport(models.TransientModel):
    _inherit = 'stock.traceability.report'

    @api.model
    def get_lines_w_user(self, line_id=None, **kw):
        context = dict(self.env.context)
        model = kw and kw['model_name'] or context.get('model')
        rec_id = kw and kw['model_id'] or context.get('active_id')
        level = kw and kw['level'] or 1
        lines = self.env['stock.move.line']
        move_line = self.env['stock.move.line']
        user = False
        if rec_id and model == 'stock.production.lot':
            lines = move_line.search([
                ('lot_id', '=', context.get('lot_name') or rec_id),
                ('state', '=', 'done'),
            ])
        elif  rec_id and model == 'stock.move.line' and context.get('lot_name'):
            record = self.env[model].browse(rec_id)
            dummy, is_used = self._get_linked_move_lines(record)
            if is_used:
                lines = is_used
        elif rec_id and model in ('stock.picking', 'mrp.production'):
            record = self.env[model].browse(rec_id)
            user = record.user_id.name
            if model == 'stock.picking':
                lines = record.move_lines.mapped('move_line_ids').filtered(lambda m: m.lot_id and m.state == 'done')
            else:
                lines = record.move_finished_ids.mapped('move_line_ids').filtered(lambda m: m.state == 'done')
        move_line_vals = self._lines(line_id, model_id=rec_id, model=model, level=level, move_lines=lines)
        final_vals = sorted(move_line_vals, key=lambda v: v['date'], reverse=True)
        lines = self._final_vals_to_lines(final_vals, level)
        return (lines, user)

    def _get_html(self):
        result = {}
        rcontext = {}
        context = dict(self.env.context)
        (rcontext['lines'], rcontext['user']) = self.with_context(context).get_lines_w_user()
        result['html'] = self.env.ref('stock.report_stock_inventory').render(rcontext)
        return result