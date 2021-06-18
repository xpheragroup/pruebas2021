from odoo import http
from odoo.http import request
from odoo.tools import ustr
from odoo.tools.translate import _


class Export(http.Controller):

    def fields_get(self, model):
        Model = request.env[model]
        fields = Model.fields_get()
        return fields

    @http.route('/web/export/get_fields', type='json', auth="user")
    def get_fields(self, model, prefix='', parent_name='',
                   import_compat=True, parent_field_type=None,
                   parent_field=None, exclude=None):
        fields = self.fields_get(model)
        if import_compat:
            if parent_field_type in ['many2one', 'many2many']:
                rec_name = request.env[model]._rec_name
                fields = {'id': fields['id'], rec_name: fields[rec_name]}
        else:
            fields['.id'] = {**fields['id']}

        fields['id']['string'] = _('External ID')

        if parent_field:
            parent_field['string'] = _('External ID')
            fields['id'] = parent_field

        fields_sequence = sorted(fields.items(),
                                 key=lambda field: ustr(field[1].get('string', '').lower()))

        records = []
        for field_name, field in fields_sequence:
            if import_compat and not field_name == 'id':
                if exclude and field_name in exclude:
                    continue
                if field.get('readonly'):
                    # If none of the field's states unsets readonly, skip the field
                    if all(dict(attrs).get('readonly', True)
                           for attrs in field.get('states', {}).values()):
                        continue
            if not field.get('exportable', True):
                continue

            id = prefix + (prefix and '/' or '') + field_name
            val = id
            if field_name == 'name' and import_compat and parent_field_type in ['many2one', 'many2many']:
                # Add name field when expand m2o and m2m fields in import-compatible mode
                val = prefix
            name = parent_name + (parent_name and '/' or '') + field['string']
            record = {'id': id, 'string': name,
                      'value': val, 'children': False,
                      'field_type': field.get('type'),
                      'required': field.get('required'),
                      'relation_field': field.get('relation_field')}
            records.append(record)

            if len(id.split('/')) < 10 and 'relation' in field:
                ref = field.pop('relation')
                record['value'] += '/id'
                record['params'] = {'model': ref, 'prefix': id,
                                    'name': name, 'parent_field': field}
                record['children'] = True

        return records
