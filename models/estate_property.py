from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
  _name = 'estate.property'
  _description = 'Estate Property'
  _order = 'id desc'

  _check_expected_price = models.Constraint(
    'CHECK(expected_price > 0)',
    'The expected price should be strict positive.'
  )
  _check_selling_price = models.Constraint(
    'CHECK(selling_price >= 0)',
    'The selling price should be positive'
  )

  name = fields.Char(required=True)
  description = fields.Text()
  postcode = fields.Char()
  date_availability = fields.Date(
    copy=False, 
    default=fields.Datetime().today()+relativedelta(months=3)
  )
  expected_price = fields.Float(required=True)
  selling_price = fields.Float(readonly=True, copy=False)
  bedrooms = fields.Integer(default=2)
  living_area = fields.Integer()
  facades = fields.Integer()
  garage = fields.Boolean()
  garden = fields.Boolean()
  garden_area = fields.Integer()
  garden_orientation = fields.Selection(
    selection=[
      ('north', 'North'),
      ('south', 'South'),
      ('east', 'East'),
      ('west', 'West'),
    ]
  )
  active = fields.Boolean(default=True)
  state = fields.Selection(
    selection=[
      ('new', 'New'),
      ('offer_received', 'Offer Received'),
      ('offer_accepted', 'Offer Accepted'),
      ('sold', 'Sold'),
      ('cancelled', 'Cancelled'),
    ],
    required=True,
    copy=False,
    default="new"
  )

  property_type_id = fields.Many2one('estate.property.type', 'Property Type')
  salesman_user_id = fields.Many2one('res.users', 'Salesman', default=lambda self: self.env.user)
  buyer_partner_id = fields.Many2one('res.partner', 'Buyer', copy=False)
  tag_ids = fields.Many2many('estate.property.tag', string='Tags')
  offer_ids = fields.One2many('estate.property.offer', 'property_id', 'Offers')

  total_area = fields.Integer(compute='_compute_total_area')
  best_offer = fields.Float(compute='_compute_best_offer')

  @api.constrains('selling_price', 'expected_price')
  def _check_price_ratio(self):
    for record in self:
      price_ratio = record.selling_price / record.expected_price
      if record.selling_price > 0 and float_compare(price_ratio, 0.9, precision_rounding=0.001) < 0:
        raise ValidationError(_('The selling price cannot lower than 90% of the expected price'))

  @api.depends('living_area', 'garden_area')
  def _compute_total_area(self):
    for record in self:
      record.total_area = record.living_area + record.garden_area

  @api.depends('offer_ids.price')
  def _compute_best_offer(self):
    for record in self:
      best_offer = 0
      if (len(record.offer_ids) > 0):
        best_offer = max(record.offer_ids.mapped('price'))
      record.best_offer = best_offer

  @api.onchange('garden')
  def _onchange_garden(self):
    if self.garden:
      self.garden_area = 10
      self.garden_orientation = 'north'
    else:
      self.garden_area = 0
      self.garden_orientation = False

  def action_sold(self):
    for record in self:
      if record.state != 'new':
        raise UserError(_(f"{record.state.replace('_', ' ').capitalize()} properties cannot be sold"))
      record.state = 'sold'
    return True

  def action_cancel(self):
    for record in self:
      if record.state != 'new':
        raise UserError(_(f"{record.state.replace('_', ' ').capitalize()} properties cannot be cancelled"))
      record.state = 'cancelled'
    return True
