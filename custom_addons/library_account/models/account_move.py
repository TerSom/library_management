from odoo import fields, models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    loan_id = fields.Many2one('library.loan', string='Library Loan', compute='_compute_loan_id', store=True, readonly=False)

    @api.depends('invoice_origin')
    def _compute_loan_id(self):
        for move in self:
            if move.invoice_origin and not move.loan_id:
                loan = self.env['library.loan'].search([('name', '=', move.invoice_origin)], limit=1)
                move.loan_id = loan.id if loan else False

    def action_view_loans(self):
        self.ensure_one()
        return {
            'name': 'Library Loans',
            'type': 'ir.actions.act_window',
            'res_model': 'library.loan',
            'view_mode': 'form',
            'res_id': self.loan_id.id,
            'target': 'current',
        }
