To use this functionality you need to return following action:

.. code-block:: python

    @api.multi
    def my_button_action():
        self.ensure_one()
        return {
            'type': 'ir.actions.act_m2m_list_row_add',
            'field_name' : 'my_m2m_field_name',
        }
