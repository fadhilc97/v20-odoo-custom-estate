from odoo import models, fields

class EstatePropertyTag(models.Model):
  _name = 'estate.property.tag'
  _description = 'Estate Property Tag'
  _order = 'name asc'
  
  _unique_name = models.Constraint(
    'UNIQUE(name)',
    'The name should unique'
  )

  name = fields.Char(required=True)