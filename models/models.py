# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import requests
import simplejson
import time
from odoo.osv import expression
import re
import dateutil.parser
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
import webbrowser


class XenditInfo(models.Model):
	_name = 'xendit.info'

	order_id = fields.Many2one('sale.order', string='Sale Order')
	account_so_url = fields.Text(string='Invoice Url',readonly=True)
	created = fields.Date(string='Date Created',readonly=True)
	bank_code = fields.Char(string='Bank Code')
	va_number = fields.Char(string='VA Number')


	@api.multi
	def redirect(self):
		webbrowser.open_new_tab(self.account_so_url)



class vit_create_xendit_so(models.Model):
	_inherit = 'sale.order'

	xendit_info_ids = fields.One2many('xendit.info', 'order_id', string='Xendit Info')
	merchant = fields.Text(string='Merchant Name',readonly=True)
	external = fields.Text(string='External Email',readonly=True)
	payment_type = fields.Selection([('va_payment','Virtual Account'),('credit_card','Credit Card')], string="Payment Type", default="va_payment")
	amount_type_pay = fields.Float(default=4000)


	@api.depends('order_line.price_total')
	def _amount_all(self):
		"""
		Compute total amount di SO dengan admin fee xendit
		"""
		for order in self:
			amount_untaxed = amount_tax = 0.0
			for line in order.order_line:
				amount_untaxed += line.price_subtotal
				amount_tax += line.price_tax
			order.update({
				'amount_untaxed': amount_untaxed,
				'amount_tax': amount_tax,
				'amount_total': amount_untaxed + amount_tax + self.amount_type_pay,
			})

	@api.multi
	def action_create_xendit_so(self):
		url = "https://api.xendit.co/v2/invoices"
		user = "xnd_development_kdzbsTmz9p1JZUcs58mcjNCDMEI7RT8mH55NIjHFhuZ2XgJGcpBk44AeBRdu5zx"

		# if self.payment_type == 'va_payment':
		# 	self.amount_type_pay = 4000
		# if self.payment_type == 'credit_card':
		# 	self.amount_type_pay = (self.amount_total * 0.0263) + 1800


		# Delete xendit info sebelum create ===================
		cr = self.env.cr
		sql = "delete from xendit_info where order_id=%s"
		cr.execute(sql, (self.id,))


		# Create xendit info ===================
		for rec in self.partner_id.partner_va_ids:
			data = {
					'external_id'	: self.name,
					'payer_email'	: self.partner_id.email,
					'description'	: "Total sudah termasuk biaya admin sebesar Rp %s" % self.amount_type_pay,
					'amount'		: self.amount_total,
					'callback_virtual_account_id'	: rec.va_external_id,
			}

			_logger.info("data ke xendit %s", data)

			act = requests.post(url, data=data, auth=(user, ''))
			res = simplejson.loads(act.text)
			_logger.info("response: %s", res)

			# Jika response error ==============================
			if 'error_code' in res:
				raise UserError(res['message'])

			# Jika response success ============================
			self.env['xendit.info'].create({
				'order_id'			: self.id,
				'account_so_url'	: res['invoice_url'],
				'created'			: res['created'],
				'bank_code'			: res['available_banks'][-1]['bank_code'],
				'va_number'			: res['available_banks'][-1]['bank_account_number'],
			})


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
			'default_model'				: 'sale.order',
			'default_res_id'			: self.ids[0],
			'default_use_template'		: bool(template_id),
			'default_template_id'		: template_id,
			'default_composition_mode'	: 'comment',
			'mark_so_as_sent'			: True,
			'force_email'				: True,
		}

		return {
			'type'			: 'ir.actions.act_window',
			'view_type'		: 'form',
			'view_mode'		: 'form',
			'res_model'		: 'mail.compose.message',
			'views'			: [(compose_form_id, 'form')],
			'view_id'		: compose_form_id,
			'target'		: 'new',
			'context'		: ctx,
		}
