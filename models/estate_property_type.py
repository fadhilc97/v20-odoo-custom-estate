from odoo import models, fields

class EstatePropertyType(models.Model):
  _name = 'estate.property.type'
  _description = 'Estate Property Type'
  _order = 'name asc'

  _unique_name = models.Constraint(
    'UNIQUE(name)',
    'The name should unique'
  )

  name = fields.Char(required=True)
  property_ids = fields.One2many('estate.property', 'property_type_id')