# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import requests
import simplejson

class vit_create_xendit_so(models.Model):
	_inherit = 'sale.order'

	account_so_url = fields.Text(string='Account Invoice Url',readonly=True)
	email = fields.Text(string='Email',readonly=True)

	@api.multi
	def action_create_xendit_so(self):
		url = "https://api.xendit.co/v2/invoices"
		user = "xnd_development_kdzbsTmz9p1JZUcs58mcjNCDMEI7RT8mH55NIjHFhuZ2XgJGcpBk44AeBRdu5zx"

		data = {
				'external_id'	:	self.name,
				'payer_email'	:	self.od_id.email,
				'description'	:	"Congratulation Mr/Mrs %s" % self.od_id.name,
				'amount'		:	self.amount_total
		}
		act = requests.post(url, data=data, auth=(user, ''))
		res = simplejson.loads(act.text)
		print(res)
		self.account_so_url = res['invoice_url']
		self.email = res['payer_email']
