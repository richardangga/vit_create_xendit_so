# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import requests
import simplejson
import datetime
import dateutil.parser
from odoo.exceptions import UserError

class vit_create_xendit_so(models.Model):
	_inherit = 'sale.order'

	account_so_url = fields.Text(string='Account Invoice Url',readonly=True)
	email = fields.Text(string='Email',readonly=True)
	merchant = fields.Text(string='Merchant Name',readonly=True)
	external = fields.Text(string='External Email',readonly=True)
	created = fields.Date(string='Date Created',readonly=True)
	expired = fields.Date(string='Expiry Date', readonly=True)
	corporate = fields.Text(string='Corporate', readonly=True)

	@api.multi
	def action_create_xendit_so(self):
		url = "https://api.xendit.co/v2/invoices"
		user = "xnd_development_kdzbsTmz9p1JZUcs58mcjNCDMEI7RT8mH55NIjHFhuZ2XgJGcpBk44AeBRdu5zx"

		data = {
				'external_id'	:	self.user_id.email,
				'payer_email'	:	self.partner_id.email,
				'description'	:	"Invoice Mr/Mrs %s" % self.partner_id.display_name,
				'amount'		:	self.amount_total
		}
		act = requests.post(url, data=data, auth=(user, ''))
		res = simplejson.loads(act.text)
		print(res)

		if 'error_code' in res:
			raise UserError(res['message'])

		self.external = res['external_id']	
		self.account_so_url = res['invoice_url']
		self.email = res['payer_email']
		self.merchant = res['merchant_name']
		self.created = res['created']
		self.expired = res['expiry_date']

		self.ensure_one()
		ir_model_data = self.env['ir.model.data']
		try:
			template_id = ir_model_data.get_object_reference('vit_create_xendit_so', 'email_xendit_so_template')[1]
		except ValueError:
			template_id = False
		try:
			compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
		except ValueError:
			compose_form_id = False
		ctx = {
			'default_model': 'sale.order',
			'default_res_id': self.ids[0],
			'default_use_template': bool(template_id),
			'default_template_id': template_id,
			'default_composition_mode': 'comment',
			'mark_so_as_sent': True,
			'force_email': True
		}
		return {
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views': [(compose_form_id, 'form')],
			'view_id': compose_form_id,
			'target': 'new',
			'context': ctx,
		}