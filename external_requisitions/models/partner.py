
from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class ResPartner(models.Model):
    _inherit = "res.partner"

    presupuesto = fields.Monetary(string='Presupuesto')
    periodo = fields.Float(string='Periodo', default=0, help='Hace referencia a los intervalos de tiempo de validez del presupuesto (ej: 1 Mes, 3 Meses, 5 Días, 2 Semanas).')
    periodos_transcurridos = fields.Float(string='Periodos Transcurridos', defaul=1, help='Periodos transcurridos.')
    periodicidad = fields.Selection([
        ('dias','Días'),
        ('semanas','Semanas'),
        ('meses','Meses'),
        ('semestres','Semestres'),
        ('años','Años')
        ], default='dias', string='Periodicidad')
    date_beging = fields.Date(string='Fecha de Inicio')
    
    def _get_amount(self):
        self.gasto_periodo = self.last_invoiced_order

    def _get_amounts_approved(self):
        if not self.ordenes:
            self.last_approved_order = 0
        for line in self.ordenes:
            if line.tax_id:
                self.last_approved_order += (line.product_uom_qty * line.price_unit) * (1 + (line.tax_id.amount / 100))
            else:
                self.last_approved_order += line.product_uom_qty * line.price_unit

    def _get_amounts_invoiced(self):
        if not self.ordenes:
            self.last_invoiced_order = 0
        for line in self.ordenes:
            if line.tax_id:
                self.last_invoiced_order += (line.qty_invoiced * line.price_unit) * (1 + (line.tax_id.amount / 100))
            else:
                self.last_invoiced_order += line.qty_invoiced * line.price_unit
    
    gasto_periodo = fields.Monetary(string='Gasto en el Periodo Actual', compute='_get_amount', help='Permite saber la cantidad ejecutada del presupuesto por periodo.')
    last_approved_order = fields.Monetary(string='Cantidad Aprobada Último Periodo', compute='_get_amounts_approved', help='Permite saber la cantidad aprobada del último pedido.')
    last_invoiced_order = fields.Monetary(string='Cantidad Facturada Último Periodo', compute='_get_amounts_invoiced', help='Permite saber la cantidad facturada del último pedido.')

    ordenes = fields.Many2many('sale.order.line', string='Ordenes')

    actual_date_beging = fields.Date(string='Fecha de Inicio Actual', compute='_date_beging', help='Fecha de inicio del periodo actual.')

    @api.depends('date_beging','periodo','periodicidad','periodos_transcurridos')
    def _date_beging(self):
        self.actual_date_beging = datetime.today()
        multiplicador = self.periodos_transcurridos * self.periodo
        if self.periodicidad == 'dias':
            if self.periodos_transcurridos == 0:
                self.actual_date_beging = self.date_beging
            else:
                self.actual_date_beging = self.date_beging + timedelta(days = multiplicador)
        elif self.periodicidad == 'semanas':
            if self.periodos_transcurridos == 0:
                self.actual_date_beging = self.date_beging
            else:
                self.actual_date_beging = self.date_beging + timedelta(days = multiplicador*7)
        elif self.periodicidad == 'meses':
            if self.periodos_transcurridos == 0:
                self.actual_date_beging = self.date_beging
            else:
                self.actual_date_beging = self.date_beging + relativedelta(months = multiplicador)
        elif self.periodicidad == 'semestres':
            if self.periodos_transcurridos == 0:
                self.actual_date_beging = self.date_beging
            else:
                self.actual_date_beging = self.date_beging + relativedelta(months = multiplicador*6)
        elif self.periodicidad == 'años':
            if self.periodos_transcurridos == 0:
                self.actual_date_beging = self.date_beging
            else:
                self.actual_date_beging = self.date_beging + relativedelta(years = multiplicador)

    actual_date_end = fields.Date(string='Fecha de Fin Actual', compute='_date_end', help='Fecha de fin del periodo actual.')

    @api.depends('date_beging','periodo','periodicidad','periodos_transcurridos','actual_date_beging')
    def _date_end(self):
        if self.actual_date_beging:
            self.actual_date_end = datetime.today() + timedelta(days = 1)
            if self.periodicidad == 'dias':
                if self.periodos_transcurridos == 0:
                    self.actual_date_end = self.actual_date_beging + timedelta(days = self.periodo)
                else:
                    self.actual_date_end = self.actual_date_beging + timedelta(days = self.periodo)
            elif self.periodicidad == 'semanas':
                if self.periodos_transcurridos == 0:
                    self.actual_date_end = self.actual_date_beging + timedelta(days = self.periodo*7)
                else:
                    self.actual_date_end = self.actual_date_beging + timedelta(days = self.periodo*7)
            elif self.periodicidad == 'meses':
                if self.periodos_transcurridos == 0:
                    self.actual_date_end = self.actual_date_beging + relativedelta(months = self.periodo)
                else:
                    self.actual_date_end = self.actual_date_beging + relativedelta(months = self.periodo)
            elif self.periodicidad == 'semestres':
                if self.periodos_transcurridos == 0:
                    self.actual_date_end = self.actual_date_beging + relativedelta(months = self.periodo*6)
                else:
                    self.actual_date_end = self.actual_date_beging + relativedelta(months = self.periodo*6)
            elif self.periodicidad == 'años':
                if self.periodos_transcurridos == 0:
                    self.actual_date_end = self.actual_date_beging + relativedelta(years = self.periodo)
                else:
                    self.actual_date_end = self.actual_date_beging + relativedelta(years = self.periodo)
        else:
            self.actual_date_end=None
    
