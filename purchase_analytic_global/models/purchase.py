# Copyright 2014-2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import Command, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    account_analytic_id = fields.Many2one(
        "account.analytic.account",
        string="Analytic Account",
        compute="_compute_analytic_account",
        inverse="_inverse_analytic_account",
        help="This account will be propagated to all lines distributions, if you need "
        "to use different distribution accounts, define the accounts at line level.",
    )

    @api.depends("order_line.distribution_analytic_account_ids")
    def _compute_analytic_account(self):
        for rec in self:
            accounts_ids = rec.mapped("order_line.distribution_analytic_account_ids")
            if len(accounts_ids) == 1:
                rec.account_analytic_id = accounts_ids
            else:
                rec.account_analytic_id = False

    def _inverse_analytic_account(self):
        for rec in self:
            if rec.account_analytic_id:
                rec.order_line.distribution_analytic_account_ids = [
                    Command.set(rec.account_analytic_id.ids)
                ]
