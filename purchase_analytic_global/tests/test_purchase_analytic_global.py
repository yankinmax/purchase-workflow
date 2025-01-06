# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import date

from odoo import Command
from odoo.tests.common import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestPurchaseAnalyticGlobal(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env["base"].with_context(**DISABLED_MAIL_CONTEXT).env
        cls.purchase_order_model = cls.env["purchase.order"]
        cls.partner_model = cls.env["res.partner"]
        cls.analytic_account_model = cls.env["account.analytic.account"]
        cls.analytic_plan = cls.env["account.analytic.plan"].create({"name": "Plan"})
        cls.partner1 = cls.partner_model.create({"name": "Partner1"})
        cls.partner2 = cls.partner_model.create({"name": "Partner2"})
        cls.analytic_account1 = cls.analytic_account_model.create(
            {"name": "Analytic Account 1", "plan_id": cls.analytic_plan.id}
        )
        cls.analytic_account2 = cls.analytic_account_model.create(
            {"name": "Analytic Account 2", "plan_id": cls.analytic_plan.id}
        )
        cls.product = cls.env.ref("product.product_product_4")
        cls.purchase_order1 = cls.purchase_order_model.create(
            {
                "partner_id": cls.partner1.id,
                "account_analytic_id": cls.analytic_account1.id,
                "order_line": [
                    Command.create(
                        {
                            "analytic_distribution": {cls.analytic_account1.id: 31},
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_qty": 10,
                            "price_unit": 50,
                            "product_uom": cls.product.uom_id.id,
                            "date_planned": date.today(),
                        }
                    )
                ],
            }
        )
        cls.purchase_order2 = cls.purchase_order_model.create(
            {
                "partner_id": cls.partner2.id,
                "order_line": [
                    Command.create(
                        {
                            "analytic_distribution": {cls.analytic_account2.id: 44},
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_qty": 5,
                            "price_unit": 40,
                            "product_uom": cls.product.uom_id.id,
                            "date_planned": date.today(),
                        }
                    )
                ],
            }
        )

    def test_purchase_order_check(self):
        self.assertEqual(
            self.purchase_order1.order_line[0].distribution_analytic_account_ids,
            self.analytic_account1,
        )
        self.assertEqual(
            self.purchase_order1.account_analytic_id,
            self.analytic_account1,
        )
        self.assertEqual(
            self.purchase_order2.order_line[0].distribution_analytic_account_ids,
            self.analytic_account2,
        )
        self.assertEqual(
            self.purchase_order2.account_analytic_id, self.analytic_account2
        )
        self.purchase_order2.write(
            {
                "order_line": [
                    Command.create(
                        {
                            "analytic_distribution": {self.analytic_account1.id: 55},
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_qty": 10,
                            "price_unit": 20,
                            "product_uom": self.product.uom_id.id,
                            "date_planned": date.today(),
                        }
                    )
                ],
            }
        )
        self.assertFalse(self.purchase_order2.account_analytic_id)
