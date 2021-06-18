odoo.define('custom_pos.models', function (require) {
    "use strict";
    var posModels = require('point_of_sale.models');
    posModels.Orderline = posModels.Orderline.extend({
        get_taxes_names: function() {
            var taxes_ids = this.get_product().taxes_id
            var product_taxes = [];
            var taxes =  this.pos.taxes;
            _(taxes_ids).each(function(el){
                var tax = _.detect(taxes, function(t){
                    return t.id === el;
                });
                product_taxes.push(tax.name);
            });
            return product_taxes;
        },
        export_for_printing: function(){
            return {
                quantity:           this.get_quantity(),
                unit_name:          this.get_unit().name,
                price:              this.get_unit_display_price(),
                discount:           this.get_discount(),
                product_name:       this.get_product().display_name,
                product_name_wrapped: this.generate_wrapped_product_name(),
                price_lst:          this.get_lst_price(),
                display_discount_policy:    this.display_discount_policy(),
                price_display_one:  this.get_display_price_one(),
                price_display :     this.get_display_price(),
                price_with_tax :    this.get_price_with_tax(),
                price_without_tax:  this.get_price_without_tax(),
                price_with_tax_before_discount:  this.get_price_with_tax_before_discount(),
                tax:                this.get_tax(),
                product_description:      this.get_product().description,
                product_description_sale: this.get_product().description_sale,
                taxes: this.get_taxes_names(),
                product_code: this.get_product().default_code,
            };
        },
    });
    
    posModels.Order = posModels.Order.extend({
        export_for_printing: function(){
            var orderlines = [];
            var self = this;
    
            this.orderlines.each(function(orderline){
                orderlines.push(orderline.export_for_printing());
            });
    
            var paymentlines = [];
            this.paymentlines.each(function(paymentline){
                paymentlines.push(paymentline.export_for_printing());
            });
            var client  = this.get('client');
            var cashier = this.pos.get_cashier();
            var company = this.pos.company;
            var date    = new Date();
    
            function is_html(subreceipt){
                return subreceipt ? (subreceipt.split('\n')[0].indexOf('<!DOCTYPE QWEB') >= 0) : false;
            }
    
            function render_html(subreceipt){
                if (!is_html(subreceipt)) {
                    return subreceipt;
                } else {
                    subreceipt = subreceipt.split('\n').slice(1).join('\n');
                    var qweb = new QWeb2.Engine();
                        qweb.debug = config.isDebug();
                        qweb.default_dict = _.clone(QWeb.default_dict);
                        qweb.add_template('<templates><t t-name="subreceipt">'+subreceipt+'</t></templates>');
    
                    return qweb.render('subreceipt',{'pos':self.pos,'widget':self.pos.chrome,'order':self, 'receipt': receipt}) ;
                }
            }
    
            var receipt = {
                orderlines: orderlines,
                paymentlines: paymentlines,
                subtotal: this.get_subtotal(),
                total_with_tax: this.get_total_with_tax(),
                total_without_tax: this.get_total_without_tax(),
                total_tax: this.get_total_tax(),
                total_paid: this.get_total_paid(),
                total_discount: this.get_total_discount(),
                tax_details: this.get_tax_details(),
                change: this.get_change(),
                name : this.get_name(),
                client: client ? client.name : null ,
                invoice_id: null,   //TODO
                cashier: cashier ? cashier.name : null,
                precision: {
                    price: 2,
                    money: 2,
                    quantity: 3,
                },
                date: {
                    year: date.getFullYear(),
                    month: date.getMonth(),
                    date: date.getDate(),       // day of the month
                    day: date.getDay(),         // day of the week
                    hour: date.getHours(),
                    minute: date.getMinutes() ,
                    isostring: date.toISOString(),
                    localestring: this.formatted_validation_date,
                },
                company:{
                    email: company.email,
                    website: company.website,
                    company_registry: company.company_registry,
                    contact_address: company.partner_id[1],
                    vat: company.vat,
                    vat_label: company.country && company.country.vat_label || '',
                    name: company.name,
                    phone: company.phone,
                    logo:  this.pos.company_logo_base64,
                },
                currency: this.pos.currency,
                numeracion_facturacion: this.pos.config.numeracion_facturacion,
                range0: this.pos.config.range0,
                range1: this.pos.config.range1,
                fact_code: this.pos.config.fact_code,
            };
    
            if (is_html(this.pos.config.receipt_header)){
                receipt.header = '';
                receipt.header_html = render_html(this.pos.config.receipt_header);
            } else {
                receipt.header = this.pos.config.receipt_header || '';
            }
    
            if (is_html(this.pos.config.receipt_footer)){
                receipt.footer = '';
                receipt.footer_html = render_html(this.pos.config.receipt_footer);
            } else {
                receipt.footer = this.pos.config.receipt_footer || '';
            }
    
            return receipt;
        },
    });
 });