# -*- coding: utf-8 -*-

from odoo import models, fields

class tracking_field_overwriter(models.Model):

    _name = 'res.partner'
    _inherit = 'res.partner'

    # Base Name
    name = fields.Char(tracking=1)
    var = fields.Char(tracking=1)
    phone = fields.Char(tracking=1)
    mobile = fields.Char(tracking=1)
    email = fields.Char(tracking=1)
    website = fields.Char(tracking=1)

    # Base Address
    street = fields.Char(tracking=1)
    street2 = fields.Char(tracking=1)
    city = fields.Char(tracking=1)
    state_id = fields.Many2one(tracking=1)
    zip = fields.Char(tracking=1)
    country_id = fields.Many2one(tracking=1)

    # Sales and purchase
    user_id = fields.Many2one(tracking=1)
    property_payment_term_id = fields.Many2one(tracking=1)
    property_supplier_payment_term_id = fields.Many2one(tracking=1)
    default_supplierinfo_discount = fields.Float(tracking=1)
    barcode = fields.Char(tracking=1)
    property_account_position_id = fields.Many2one(tracking=1)
    ref = fields.Char(tracking=1)
    company_id = fields.Many2one(tracking=1)
    website_id = fields.Many2one(tracking=1)
    industry_id = fields.Many2one(tracking=1)
    property_stock_customer = fields.Many2one(tracking=1)
    property_stock_supplier = fields.Many2one(tracking=1)

    # Accounting
    bank_ids = fields.One2many(tracking=1)
    property_account_receivable_id = fields.Many2one(tracking=1)
    property_account_payable_id = fields.Many2one(tracking=1)

    # Internal notes
    comment = fields.Text(tracking=1)

    # 2Many fields 
    def write(self, vals):
        write_result = super(tracking_field_overwriter, self).write(vals)
        if write_result:
            if vals.get('bank_ids') is not None:
                for bank_ids_change in vals['bank_ids']:
                    if bank_ids_change[2]:
                        if 'acc_number' in bank_ids_change[2]:
                            message = 'Se ha cambiado el número de la cuenta bancaria a {}.'
                            self.message_post(body=message.format(bank_ids_change[2]['acc_number']))
                        if 'bank_id' in bank_ids_change[2]:
                            message = 'Se ha cambiado la cuenta bancaria a {}.'
                            bank_name = self.env['res.bank'].search([['id','=',bank_ids_change[2]['bank_id']]]).name
                            self.message_post(body=message.format(bank_name))
            if vals.get('child_ids') is not None:
                self.message_post(body='Se ha cambiado la información de los contactos.')
            if vals.get('active') is not None:
                if vals['active']:
                    self.message_post(body='El estado del contacto ha pasado a dearchivado.')
                else:
                    self.message_post(body='El estado del contacto ha pasado a archivado.')
        return write_result


class ProductOver(models.Model):
    _inherit = 'product.template'

    name = fields.Char(tracking=1)
    sequence = fields.Integer(tracking=1)
    description = fields.Text(tracking=1)
    description_purchase = fields.Text(tracking=1)
    description_sale = fields.Text(tracking=1)
    type = fields.Selection(tracking=1)
    rental = fields.Boolean(tracking=1)
    categ_id = fields.Many2one(tracking=1)
    currency_id = fields.Many2one(tracking=1)
    cost_currency_id = fields.Many2one(tracking=1)

    # price fields
    # price: total template price, context dependent (partner, pricelist, quantity)
    price = fields.Float(tracking=1)
    # list_price: catalog price, user defined
    list_price = fields.Float(tracking=1)
    # lst_price: catalog price for template, but including extra for variants
    lst_price = fields.Float(tracking=1)
    standard_price = fields.Float(tracking=1)

    volume = fields.Float(tracking=1)
    weight = fields.Float(tracking=1)
    weight_uom_name = fields.Char(tracking=1)

    sale_ok = fields.Boolean(tracking=1)
    purchase_ok = fields.Boolean(tracking=1)
    pricelist_id = fields.Many2one(tracking=1)
    uom_id = fields.Many2one(tracking=1)
    uom_name = fields.Char(tracking=1)
    uom_po_id = fields.Many2one(tracking=1)
    company_id = fields.Many2one(tracking=1)
    packaging_ids = fields.One2many(tracking=1)
    seller_ids = fields.One2many(tracking=1)
    variant_seller_ids = fields.One2many(tracking=1)

    #active = fields.Boolean(tracking=1)
    color = fields.Integer(tracking=1)

    is_product_variant = fields.Boolean(tracking=1)
    attribute_line_ids = fields.One2many(tracking=1)

    valid_product_template_attribute_line_ids = fields.Many2many(tracking=1)

    product_variant_ids = fields.One2many(tracking=1)
    # performance: product_variant_id provides prefetching on the first product variant only
    product_variant_id = fields.Many2one(tracking=1)

    product_variant_count = fields.Integer(tracking=1)

    # related to display product product information if is_product_variant
    barcode = fields.Char(tracking=1)
    default_code = fields.Char(tracking=1)

    pricelist_item_count = fields.Integer(tracking=1)

    can_image_1024_be_zoomed = fields.Boolean(tracking=1)
    has_configurable_attributes = fields.Boolean(tracking=1)

    #Stock

    responsible_id = fields.Many2one(tracking=1)
    property_stock_production = fields.Many2one(tracking=1)
    property_stock_inventory = fields.Many2one(tracking=1)
    sale_delay = fields.Float(tracking=1)
    tracking = fields.Selection(tracking=1)
    description_picking = fields.Text(tracking=1)
    description_pickingout = fields.Text(tracking=1)
    description_pickingin = fields.Text(tracking=1)
    qty_available = fields.Float(tracking=1)
    virtual_available = fields.Float(tracking=1)
    incoming_qty = fields.Float(tracking=1)
    outgoing_qty = fields.Float(tracking=1)
    # The goal of these fields is to be able to put some keys in context from search view in order
    # to influence computed field.
    location_id = fields.Many2one(tracking=1)
    warehouse_id = fields.Many2one(tracking=1)
    route_ids = fields.Many2many(tracking=1)
    nbr_reordering_rules = fields.Integer(tracking=1)
    reordering_min_qty = fields.Float(tracking=1)
    reordering_max_qty = fields.Float(tracking=1)
    # TDE FIXME: seems only visible in a view - remove me ?
    route_from_categ_ids = fields.Many2many(tracking=1)

    # 2Many fields 
    def write(self, vals):
        write_result = super(ProductOver, self).write(vals)
        if write_result:
            if vals.get('active') is not None:
                if vals['active']:
                    self.message_post(body='El estado del producto ha pasado a dearchivado.')
                else:
                    self.message_post(body='El estado del producto ha pasado a archivado.')

class ProductionOver(models.Model):
    _inherit = 'mrp.production'

    # 2Many fields
    def write(self, vals):
        write_result = super(ProductionOver, self).write(vals)
        if write_result:
            if vals.get('move_raw_ids') is not None:
                message = '<p>Se han hecho los siguientes cambios a la receta:</p><ul>'
                mods = 0
                for component in vals['move_raw_ids']:
                    if component[2] != False:
                        mods += 1
                        if 'virtual' in str(component[1]):
                            message += '<li>Se agrega el producto {}.</li>'.format(component[2]['name'])
                        elif component[2].get('product_uom_qty') is not None:
                            move = self.env['stock.move'].search([['id', '=', component[1]]])
                            message += '<li>Se modifica la cantidad a usar del producto {}. De {} a {}.</li>'.format(move.product_tmpl_id.name, move.product_uom_qty, component[2]['product_uom_qty'])
                message += '</ul>'
                if mods > 0:
                    self.message_post(body=message)


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = ["product.category","mail.thread"]

    name = fields.Char(tracking=1)
    parent_id = fields.Many2one(tracking=1)
    company_id = fields.Many2one(tracking=1)
    route_ids = fields.Many2many(tracking=1)
    total_route_ids = fields.Many2many(tracking=1)
    removal_strategy_id = fields.Many2one(tracking=1)
    property_account_creditor_price_difference_categ = fields.Many2one(tracking=1)
    property_account_income_categ_id = fields.Many2one(tracking=1)
    property_account_expense_categ_id = fields.Many2one(tracking=1)
    property_stock_account_input_categ_id = fields.Many2one(tracking=1)
    property_stock_account_output_categ_id = fields.Many2one(tracking=1)
    property_stock_valuation_account_id = fields.Many2one(tracking=1)
    property_stock_journal = fields.Many2one(tracking=1)

class TransferModel(models.Model):
    _name = "account.transfer.model"
    _inherit = ["account.transfer.model","mail.thread"]

    name = fields.Char(tracking=1)
    journal_id = fields.Many2one(tracking=1)
    company_id = fields.Many2one(tracking=1)
    date_start = fields.Date(tracking=1)
    date_stop = fields.Date(tracking=1)
    frequency = fields.Selection(tracking=1)
    account_ids = fields.Many2many(tracking=1)
    line_ids = fields.One2many(tracking=1)
    move_ids = fields.One2many(tracking=1)
    move_ids_count = fields.Integer(tracking=1)
    total_percent = fields.Float(tracking=1)
    state = fields.Selection(tracking=1)

class AccountAnalyticLine(models.Model):
    _name = "account.analytic.line"
    _inherit = ["account.analytic.line","mail.thread"]

    name = fields.Char(tracking=1)
    date = fields.Date(tracking=1)
    amount = fields.Monetary(tracking=1)
    unit_amount = fields.Float(tracking=1)
    product_uom_id = fields.Many2one(tracking=1)
    product_uom_category_id = fields.Many2one(tracking=1)
    account_id = fields.Many2one(tracking=1)
    partner_id = fields.Many2one(tracking=1)
    user_id = fields.Many2one(tracking=1)
    tag_ids = fields.Many2many(tracking=1)
    company_id = fields.Many2one(tracking=1)
    currency_id = fields.Many2one(tracking=1)
    group_id = fields.Many2one(tracking=1)
    so_line = fields.Many2one(tracking=1)
    product_id = fields.Many2one(tracking=1)
    general_account_id = fields.Many2one(tracking=1)
    move_id = fields.Many2one(tracking=1)
    code = fields.Char(tracking=1)
    ref = fields.Char(tracking=1)
    task_id = fields.Many2one(tracking=1)
    project_id = fields.Many2one(tracking=1)
    employee_id = fields.Many2one(tracking=1)
    department_id = fields.Many2one(tracking=1)
    encoding_uom_id = fields.Many2one(tracking=1)
    holiday_id = fields.Many2one(tracking=1)
    timesheet_invoice_id = fields.Many2one(tracking=1)
    helpdesk_ticket_id = fields.Many2one(tracking=1)
    employee_id = fields.Many2one(tracking=1)
    amount = fields.Monetary(tracking=1)
    validated = fields.Boolean(tracking=1)
    is_timesheet = fields.Boolean(tracking=1)

class AccountPaymentTerm(models.Model):
    _name = "account.payment.term"
    _inherit = ["account.payment.term","mail.thread"]

    name = fields.Char(tracking=1)
    active = fields.Boolean(tracking=1)
    note = fields.Text(tracking=1)
    line_ids = fields.One2many(tracking=1)
    company_id = fields.Many2one(tracking=1)
    sequence = fields.Integer(tracking=1)

class AccountTax(models.Model):
    _name = "account.tax"
    _inherit = ["account.tax","mail.thread"]

    name = fields.Char(tracking=1)
    type_tax_use = fields.Selection(tracking=1)
    amount_type = fields.Selection(tracking=1)
    active = fields.Boolean(tracking=1)
    company_id = fields.Many2one(tracking=1)
    children_tax_ids = fields.Many2many(tracking=1)
    sequence = fields.Integer(tracking=1)
    amount = fields.Float(tracking=1)
    description = fields.Char(tracking=1)
    price_include = fields.Boolean(tracking=1)
    include_base_amount = fields.Boolean(tracking=1)
    analytic = fields.Boolean(tracking=1)
    tax_group_id = fields.Many2one(tracking=1)
    hide_tax_exigibility = fields.Boolean(tracking=1)
    tax_exigibility = fields.Selection(tracking=1)
    cash_basis_transition_account_id = fields.Many2one(tracking=1)
    cash_basis_base_account_id = fields.Many2one(tracking=1)
    invoice_repartition_line_ids = fields.One2many(tracking=1)
    refund_repartition_line_ids = fields.One2many(tracking=1)
    country_id = fields.Many2one(tracking=1)
    l10n_it_has_exoneration = fields.Boolean(tracking=1)
    l10n_it_law_reference = fields.Char(tracking=1)
    l10n_cl_sii_code = fields.Integer(tracking=1)
    tax_discount = fields.Boolean(tracking=1)
    base_reduction = fields.Float(tracking=1)
    amount_mva = fields.Float(tracking=1)
    l10n_in_reverse_charge = fields.Boolean(tracking=1)
    amount_type = fields.Selection(tracking=1)
    python_compute = fields.Text(tracking=1)
    python_applicable = fields.Text(tracking=1)
    l10n_de_datev_code = fields.Char(tracking=1)
    l10n_co_edi_type = fields.Many2one(tracking=1)
    l10n_co_edi_country_code = fields.Char(tracking=1)

class AccountFiscalPosition(models.Model):
    _name = "account.fiscal.position"
    _inherit = ["account.fiscal.position","mail.thread"]

    sequence = fields.Integer(tracking=1)
    name = fields.Char(tracking=1)
    active = fields.Boolean(tracking=1)
    company_id = fields.Many2one(tracking=1)
    account_ids = fields.One2many(tracking=1)
    tax_ids = fields.One2many(tracking=1)
    note = fields.Text(tracking=1)
    auto_apply = fields.Boolean(tracking=1)
    vat_required = fields.Boolean(tracking=1)
    country_id = fields.Many2one(tracking=1)
    country_group_id = fields.Many2one(tracking=1)
    state_ids = fields.Many2many(tracking=1)
    zip_from = fields.Char(tracking=1)
    zip_to = fields.Char(tracking=1)
    states_count = fields.Integer(tracking=1)
    is_taxcloud_configured = fields.Boolean(tracking=1)
    is_taxcloud = fields.Boolean(tracking=1)

class AccountJournal(models.Model):
    _inherit = "account.journal"

    name = fields.Char(tracking=1)
    code = fields.Char(tracking=1)
    active = fields.Boolean(tracking=1)
    type = fields.Selection(tracking=1)
    type_control_ids = fields.Many2many(tracking=1)
    account_control_ids = fields.Many2many(tracking=1)
    default_credit_account_id = fields.Many2one(tracking=1)
    default_debit_account_id = fields.Many2one(tracking=1)
    restrict_mode_hash_table = fields.Boolean(tracking=1)
    sequence_id = fields.Many2one(tracking=1)
    refund_sequence_id = fields.Many2one(tracking=1)
    sequence = fields.Integer(tracking=1)
    sequence_number_next = fields.Integer(tracking=1)
    refund_sequence_number_next = fields.Integer(tracking=1)
    invoice_reference_type = fields.Selection(tracking=1)
    invoice_reference_model = fields.Selection(tracking=1)
    currency_id = fields.Many2one(tracking=1)
    company_id = fields.Many2one(tracking=1)
    refund_sequence = fields.Boolean(tracking=1)
    inbound_payment_method_ids = fields.Many2many(tracking=1)
    outbound_payment_method_ids = fields.Many2many(tracking=1)
    at_least_one_inbound = fields.Boolean(tracking=1)
    at_least_one_outbound = fields.Boolean(tracking=1)
    profit_account_id = fields.Many2one(tracking=1)
    loss_account_id = fields.Many2one(tracking=1)
    company_partner_id = fields.Many2one(tracking=1)
    bank_account_id = fields.Many2one(tracking=1)
    bank_statements_source = fields.Selection(tracking=1)
    bank_acc_number = fields.Char(tracking=1)
    bank_id = fields.Many2one(tracking=1)
    post_at = fields.Selection(tracking=1)
    alias_id = fields.Many2one(tracking=1)
    alias_domain = fields.Char(tracking=1)
    alias_name = fields.Char(tracking=1)
    journal_group_ids = fields.Many2many(tracking=1)
    secure_sequence_id = fields.Many2one(tracking=1)
    kanban_dashboard = fields.Text(tracking=1)
    kanban_dashboard_graph = fields.Text(tracking=1)
    json_activity_data = fields.Text(tracking=1)
    show_on_dashboard = fields.Boolean(tracking=1)
    color = fields.Integer(tracking=1)
    check_manual_sequencing = fields.Boolean(tracking=1)
    check_sequence_id = fields.Many2one(tracking=1)
    check_next_number = fields.Char(tracking=1)
    check_printing_payment_method_selected = fields.Boolean(tracking=1)
    l10n_ar_afip_pos_number = fields.Integer(tracking=1)
    l10n_ar_afip_pos_partner_id = fields.Many2one(tracking=1)
    l10n_ar_share_sequences = fields.Boolean(tracking=1)
    l10n_in_import_export = fields.Boolean(tracking=1)
    l10n_in_gstin_partner_id = fields.Many2one(tracking=1)
    l10n_latam_use_documents = fields.Boolean(tracking=1)
    l10n_latam_company_use_documents = fields.Boolean(tracking=1)
    l10n_latam_country_code = fields.Char(tracking=1)
    l10n_ch_postal = fields.Char(tracking=1)
    l10n_se_invoice_ocr_length = fields.Integer(tracking=1)
    pos_payment_method_ids = fields.One2many(tracking=1)
    l10n_cl_point_of_sale_number = fields.Integer(tracking=1)
    l10n_cl_point_of_sale_name = fields.Char(tracking=1)
    l10n_co_edi_dian_authorization_number = fields.Char(tracking=1)
    l10n_co_edi_dian_authorization_date = fields.Date(tracking=1)
    l10n_co_edi_dian_authorization_end_date = fields.Date(tracking=1)
    l10n_co_edi_min_range_number = fields.Integer(tracking=1)
    l10n_co_edi_max_range_number = fields.Integer(tracking=1)
    l10n_co_edi_debit_note = fields.Boolean(tracking=1)
    l10n_mx_address_issued_id = fields.Many2one(tracking=1)
    l10n_mx_edi_payment_method_id = fields.Many2one(tracking=1)

class AccountAccount(models.Model):
    _name = "account.account"
    _inherit = ["account.account","mail.thread"]

    name = fields.Char(tracking=1)
    currency_id = fields.Many2one(tracking=1)
    code = fields.Char(tracking=1)
    deprecated = fields.Boolean(tracking=1)
    used = fields.Boolean(tracking=1)
    user_type_id = fields.Many2one(tracking=1)
    internal_type = fields.Selection(tracking=1)
    internal_group = fields.Selection(tracking=1)
    reconcile = fields.Boolean(tracking=1)
    tax_ids = fields.Many2many(tracking=1)
    note = fields.Text(tracking=1)
    company_id = fields.Many2one(tracking=1)
    tag_ids = fields.Many2many(tracking=1)
    group_id = fields.Many2one(tracking=1)
    root_id = fields.Many2one(tracking=1)
    opening_debit = fields.Monetary(tracking=1)
    opening_credit = fields.Monetary(tracking=1)
    asset_model = fields.Many2one(tracking=1)
    can_create_asset = fields.Boolean(tracking=1)
    form_view_ref = fields.Char(tracking=1)
    consolidation_color = fields.Integer(tracking=1)

class AccountReconcileModel(models.Model):
    _name = "account.reconcile.model"
    _inherit = ["account.reconcile.model","mail.thread"]

    name = fields.Char(tracking=1)
    sequence = fields.Integer(tracking=1)
    company_id = fields.Many2one(tracking=1)
    auto_reconcile = fields.Boolean(tracking=1)
    to_check = fields.Boolean(tracking=1)
    match_journal_ids = fields.Many2many(tracking=1)
    match_amount_min = fields.Float(tracking=1)
    match_amount_max = fields.Float(tracking=1)
    match_label_param = fields.Char(tracking=1)
    match_note_param = fields.Char(tracking=1)
    match_transaction_type_param = fields.Char(tracking=1)
    match_same_currency = fields.Boolean(tracking=1)
    match_total_amount = fields.Boolean(tracking=1)
    match_total_amount_param = fields.Float(tracking=1)
    match_partner = fields.Boolean(tracking=1)
    match_partner_ids = fields.Many2many(tracking=1)
    match_partner_category_ids = fields.Many2many(tracking=1)
    account_id = fields.Many2one(tracking=1)
    journal_id = fields.Many2one(tracking=1)
    label = fields.Char(tracking=1)
    show_force_tax_included = fields.Boolean(tracking=1)
    force_tax_included = fields.Boolean(tracking=1)
    amount = fields.Float(tracking=1)
    amount_from_label_regex = fields.Char(tracking=1)
    decimal_separator = fields.Char(tracking=1)
    tax_ids = fields.Many2many(tracking=1)
    analytic_account_id = fields.Many2one(tracking=1)
    analytic_tag_ids = fields.Many2many(tracking=1)
    has_second_line = fields.Boolean(tracking=1)
    second_account_id = fields.Many2one(tracking=1)
    second_journal_id = fields.Many2one(tracking=1)
    second_label = fields.Char(tracking=1)
    show_second_force_tax_included = fields.Boolean(tracking=1)
    force_second_tax_included = fields.Boolean(tracking=1)
    second_amount = fields.Float(tracking=1)
    second_amount_from_label_regex = fields.Char(tracking=1)
    second_tax_ids = fields.Many2many(tracking=1)
    second_analytic_account_id = fields.Many2one(tracking=1)
    second_analytic_tag_ids = fields.Many2many(tracking=1)
    number_entries = fields.Integer(tracking=1)
    activity_type_id = fields.Many2one(tracking=1)

class AccountFiscalYear(models.Model):
    _name = "account.fiscal.year"
    _inherit = ["account.fiscal.year","mail.thread"]

    name = fields.Char(tracking=1)
    date_from = fields.Date(tracking=1)
    date_to = fields.Date(tracking=1)
    company_id = fields.Many2one(tracking=1)

class AccountBudgetPost(models.Model):
    _name = "account.budget.post"
    _inherit = ["account.budget.post","mail.thread"]

    name = fields.Char(tracking=1)
    account_ids = fields.Many2many(tracking=1)
    company_id = fields.Many2one(tracking=1)

class AccountAnalyticTag(models.Model):
    _name = "account.analytic.tag"
    _inherit = ["account.analytic.tag","mail.thread"]

    name = fields.Char(tracking=1)
    color = fields.Integer(tracking=1)
    active = fields.Boolean(tracking=1)
    active_analytic_distribution = fields.Boolean(tracking=1)
    analytic_distribution_ids = fields.One2many(tracking=1)
    company_id = fields.Many2one(tracking=1)

class AccountAnalyticGroup(models.Model):
    _name = "account.analytic.group"
    _inherit = ["account.analytic.group","mail.thread"]

    name = fields.Char(tracking=1)
    description = fields.Text(tracking=1)
    parent_id = fields.Many2one(tracking=1)
    parent_path = fields.Char(tracking=1)
    children_ids = fields.One2many(tracking=1)
    complete_name = fields.Char(tracking=1)
    company_id = fields.Many2one(tracking=1)

class ResPartnerBank(models.Model):
    _name = "res.partner.bank"
    _inherit = ["res.partner.bank","mail.thread"]

    acc_number = fields.Char(tracking=1)
    sanitized_acc_number = fields.Char(tracking=1)
    acc_holder_name = fields.Char(tracking=1)
    partner_id = fields.Many2one(tracking=1)
    bank_id = fields.Many2one(tracking=1)
    bank_name = fields.Char(tracking=1)
    bank_bic = fields.Char(tracking=1)
    sequence = fields.Integer(tracking=1)
    currency_id = fields.Many2one(tracking=1)
    company_id = fields.Many2one(tracking=1)
    qr_code_valid = fields.Boolean(tracking=1)
    l10n_ch_postal = fields.Char(tracking=1)
    l10n_ch_isr_subscription_chf = fields.Char(tracking=1)
    l10n_ch_isr_subscription_eur = fields.Char(tracking=1)
    l10n_ch_show_subscription = fields.Boolean(tracking=1)
    l10n_ch_qr_iban = fields.Char(tracking=1)
    aba_routing = fields.Char(tracking=1)
    journal_id = fields.One2many(tracking=1)
    l10n_mx_edi_clabe = fields.Char(tracking=1)
    aba_bsb = fields.Char(tracking=1)