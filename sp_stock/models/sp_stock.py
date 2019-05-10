# -*- coding: utf-8 -*-

from odoo import api, models


class SpStockMove(models.Model):
    _inherit = "stock.move"

    # business methods
    @api.multi
    def _get_accounting_data_for_valuation(self):
        journal_id, acc_src, acc_dest, acc_valuation = super(SpStockMove, self)._get_accounting_data_for_valuation()
        if self.location_id.scrap_location and self.product_id.categ_id.scrap_account_id:
            acc_dest = self.product_id.categ_id.scrap_account_id.id
        return journal_id, acc_src, acc_dest, acc_valuation
