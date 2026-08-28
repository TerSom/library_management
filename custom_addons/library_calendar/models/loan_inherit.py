from odoo import models,fields,api

class LibraryLoan(models.Model):
    _inherit = 'library.loan'

    calendar_event_id = fields.Many2one('calendar.event', string="Jadwal Pengembalian", readonly=True)

    def action_confirm(self):
        res = super().action_confirm()
     
        for record in self:
            if record.date_return_expected and not record.calendar_event_id:

                event_vals = {
                    'name' : f'Deadline Pengembalian Buku:{record.name}',
                    'start': record.date_return_expected,
                    'stop': record.date_return_expected,
                    'allday' : True,
                    'description': f'Mengingatkan untuk mengembalikan buku dari referensi peminjaman {record.name}.',
                    'partner_ids': [(4, record.member_id.partner_id.id), (4, self.env.user.partner_id.id)],
                }
                new_event = self.env['calendar.event'].create(event_vals)
                record.calendar_event_id = new_event.id

        return res