To use this functionality you need to return following action:

.. code-block:: python

    @api.multi
    def my_button_action():
        self.ensure_one()
        m2m_field_name = 'my_m2m_field_name'
        no_create = False # or True if wanted
        return {
            'type' : 'ir.actions.act_m2m_list_row_add',
            'res_model' : self._name,
            'no_create' : no_create,
            'field' : {
                'name' : m2m_field_name,
                'domain' : self.fields_get(m2m_field_name)[m2m_field_name]['domain'],
                'string' : self.fields_get(m2m_field_name)[m2m_field_name]['string'],
                'value' : {
                    'res_ids' : self[m2m_field_name].ids,
                }
            }
        }
