from odoo import models, fields, api

class LibraryMember(models.Model):
    _name = 'library.member'
    _description = 'Library Member'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _inherits = {'res.partner' : 'partner_id'}

    partner_id = fields.Many2one('res.partner', string="Partner", required=True, ondelete='cascade')
    member_number = fields.Char(string='Member Number', required=True, tracking=True)

    member_type = fields.Selection([
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('general', 'General')
    ], string='Member Type', default='general', required=True, tracking=True)

    max_loan_limit = fields.Integer(
        string='Max Loan Limit',
        compute='_compute_max_loan_limit',
        store=True,
        readonly=False,
        tracking=True
    )

    @api.depends('member_type')
    def _compute_max_loan_limit(self):
        limits = {'student': 3, 'teacher': 10, 'general': 5}
        for record in self:
            record.max_loan_limit = limits.get(record.member_type, 5)

    _sql_constraints = [
        ('member_number_unique', 'UNIQUE(member_number)', 'Member number must be unique.'),
    ]
    registration_date = fields.Date(string='Registration Date', default=fields.Date.context_today)

    loan_ids = fields.One2many("library.loan", "member_id", string="Loans")
    active_loan_count = fields.Integer(string='Pinjaman Aktif', compute='_compute_loan_stats', store=True)
    total_loan_count = fields.Integer(string='Total Pinjaman', compute='_compute_loan_stats', store=True)

    @api.depends('loan_ids.state')
    def _compute_loan_stats(self):
        for record in self:
            record.total_loan_count = len(record.loan_ids)
            record.active_loan_count = len(record.loan_ids.filtered(lambda l: l.state == 'ongoing'))

    def action_view_member_loans(self):
        self.ensure_one()
        return {
            'name': f'Peminjaman: {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'library.loan',
            'view_mode': 'list,kanban,form',
            'domain': [('member_id', '=', self.id)],
            'context': {'default_member_id': self.id},
        }
