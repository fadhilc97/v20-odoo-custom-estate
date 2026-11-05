from odoo import api, models, fields
from dateutil.relativedelta import relativedelta

class EstatePropertyOffer(models.Model):
  _name = 'estate.property.offer'
  _description = 'Estate Property Offer'

  _check_price = models.Constraint(
    'CHECK(price > 0)',
    'The offer price should be strict positive'
  )

  price = fields.Float()
  status = fields.Selection([
    ('accepted', 'Accepted'),
    ('refused', 'Refused')
  ], copy=False)
  partner_id = fields.Many2one('res.partner', 'Partner', required=True)
  property_id = fields.Many2one('estate.property', 'Property', required=True)
  validity = fields.Integer(default=7)
  date_deadline = fields.Date(compute='_compute_date_deadline', inverse='_inverse_date_deadline')

  @api.depends('validity')
  def _compute_date_deadline(self):
    for record in self:
      create_date = record.create_date or fields.Datetime.today()
      record.date_deadline = create_date + relativedelta(days=record.validity)

  def _inverse_date_deadline(self):
    for record in self:
      create_date = record.create_date.date() or fields.Date.today()
      validity_delta = record.date_deadline - create_date
      record.validity = validity_delta.days

  def action_accept(self):
    for record in self:
      record.property_id.selling_price = record.price
      record.property_id.buyer_partner_id = record.partner_id
      record.status = 'accepted'
    return True

  def action_refuse(self):
    for record in self:
      record.status = 'refused'
    return True
      
