import base64
import io

from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.misc import xlsxwriter


class LoanExcelReportWizard(models.TransientModel):
    _name = "loan.excel.report.wizard"
    _description = "Library Loan Excel Report"

    date_from = fields.Date(string="From Date", required=True)
    date_to = fields.Date(string="To Date", required=True)
    state = fields.Selection(
        selection=[
            ("ongoing", "Ongoing"),
            ("returned", "Returned"),
        ],
        string="Status",
        help="Kosongkan untuk menyertakan semua peminjaman yang sudah dikonfirmasi.",
    )

    def action_export_excel(self):
        self.ensure_one()
        if self.date_from > self.date_to:
            raise ValidationError(_("From Date cannot be greater than To Date."))

        domain = [
            ("date_borrow", ">=", self.date_from),
            ("date_borrow", "<=", self.date_to),
            ("state", "in", ("ongoing", "returned")),
        ]
        if self.state:
            domain.append(("state", "=", self.state))

        loans = self.env["library.loan"].search(domain, order="date_borrow, name")
        if not loans:
            raise ValidationError(_("No confirmed loans found for selected filters."))

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})

        # Palette: Crimson / Burgundy Red Theme
        c_crimson = "#A80000"
        c_pink_zebra = "#FCE8E6"
        c_white = "#FFFFFF"
        c_border = "#E0B4B4"
        c_border_header = "#7A0000"
        c_overdue_bg = "#FFD2D2"
        c_overdue_text = "#990000"

        title_format = workbook.add_format({
            "bold": True,
            "font_name": "Segoe UI",
            "font_size": 15,
            "font_color": c_crimson,
            "align": "center",
            "valign": "vcenter",
        })
        meta_label_format = workbook.add_format({
            "bold": True,
            "font_name": "Segoe UI",
            "font_size": 10,
            "font_color": c_crimson,
            "valign": "vcenter",
        })
        meta_val_date = workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "num_format": "yyyy-mm-dd",
            "valign": "vcenter",
            "align": "left",
        })
        meta_val_text = workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "valign": "vcenter",
            "align": "left",
        })
        header_format = workbook.add_format({
            "bold": True,
            "font_name": "Segoe UI",
            "font_size": 10,
            "font_color": c_white,
            "bg_color": c_crimson,
            "border": 1,
            "border_color": c_border_header,
            "align": "center",
            "valign": "vcenter",
            "text_wrap": True,
        })

        # Formats for data rows
        cell_c_white = workbook.add_format({
            "font_name": "Segoe UI", "font_size": 9.5, "border": 1,
            "border_color": c_border, "bg_color": c_white,
            "valign": "vcenter", "align": "center"
        })
        cell_l_white = workbook.add_format({
            "font_name": "Segoe UI", "font_size": 9.5, "border": 1,
            "border_color": c_border, "bg_color": c_white,
            "valign": "vcenter", "align": "left"
        })
        wrap_l_white = workbook.add_format({
            "font_name": "Segoe UI", "font_size": 9.5, "border": 1,
            "border_color": c_border, "bg_color": c_white,
            "valign": "vcenter", "align": "left", "text_wrap": True
        })
        date_white = workbook.add_format({
            "font_name": "Segoe UI", "font_size": 9.5, "border": 1,
            "border_color": c_border, "bg_color": c_white,
            "num_format": "yyyy-mm-dd", "valign": "vcenter", "align": "center"
        })
        money_white = workbook.add_format({
            "font_name": "Segoe UI", "font_size": 9.5, "border": 1,
            "border_color": c_border, "bg_color": c_white,
            "num_format": '"Rp" #,##0', "valign": "vcenter", "align": "right"
        })

        cell_c_pink = workbook.add_format({
            "font_name": "Segoe UI", "font_size": 9.5, "border": 1,
            "border_color": c_border, "bg_color": c_pink_zebra,
            "valign": "vcenter", "align": "center"
        })
        cell_l_pink = workbook.add_format({
            "font_name": "Segoe UI", "font_size": 9.5, "border": 1,
            "border_color": c_border, "bg_color": c_pink_zebra,
            "valign": "vcenter", "align": "left"
        })
        wrap_l_pink = workbook.add_format({
            "font_name": "Segoe UI", "font_size": 9.5, "border": 1,
            "border_color": c_border, "bg_color": c_pink_zebra,
            "valign": "vcenter", "align": "left", "text_wrap": True
        })
        date_pink = workbook.add_format({
            "font_name": "Segoe UI", "font_size": 9.5, "border": 1,
            "border_color": c_border, "bg_color": c_pink_zebra,
            "num_format": "yyyy-mm-dd", "valign": "vcenter", "align": "center"
        })
        money_pink = workbook.add_format({
            "font_name": "Segoe UI", "font_size": 9.5, "border": 1,
            "border_color": c_border, "bg_color": c_pink_zebra,
            "num_format": '"Rp" #,##0', "valign": "vcenter", "align": "right"
        })

        cell_c_overdue = workbook.add_format({
            "font_name": "Segoe UI", "font_size": 9.5, "border": 1,
            "border_color": c_border, "bg_color": c_overdue_bg,
            "font_color": c_overdue_text, "bold": True,
            "valign": "vcenter", "align": "center"
        })
        cell_l_overdue = workbook.add_format({
            "font_name": "Segoe UI", "font_size": 9.5, "border": 1,
            "border_color": c_border, "bg_color": c_overdue_bg,
            "font_color": c_overdue_text, "valign": "vcenter", "align": "left"
        })
        wrap_l_overdue = workbook.add_format({
            "font_name": "Segoe UI", "font_size": 9.5, "border": 1,
            "border_color": c_border, "bg_color": c_overdue_bg,
            "font_color": c_overdue_text, "valign": "vcenter", "align": "left", "text_wrap": True
        })
        date_overdue = workbook.add_format({
            "font_name": "Segoe UI", "font_size": 9.5, "border": 1,
            "border_color": c_border, "bg_color": c_overdue_bg,
            "font_color": c_overdue_text, "bold": True,
            "num_format": "yyyy-mm-dd", "valign": "vcenter", "align": "center"
        })
        money_overdue = workbook.add_format({
            "font_name": "Segoe UI", "font_size": 9.5, "border": 1,
            "border_color": c_border, "bg_color": c_overdue_bg,
            "font_color": c_overdue_text, "bold": True,
            "num_format": '"Rp" #,##0', "valign": "vcenter", "align": "right"
        })

        summary_title_format = workbook.add_format({
            "bold": True, "font_name": "Segoe UI", "font_size": 10,
            "font_color": c_white, "bg_color": c_crimson,
            "border": 1, "border_color": c_border_header,
            "align": "center", "valign": "vcenter"
        })
        summary_label_format = workbook.add_format({
            "bold": True, "font_name": "Segoe UI", "font_size": 9.5,
            "bg_color": c_pink_zebra, "border": 1,
            "border_color": c_border, "align": "center", "valign": "vcenter"
        })
        summary_value_format = workbook.add_format({
            "bold": True, "font_name": "Segoe UI", "font_size": 9.5,
            "border": 1, "border_color": c_border,
            "align": "center", "valign": "vcenter"
        })
        summary_money_format = workbook.add_format({
            "bold": True, "font_name": "Segoe UI", "font_size": 9.5,
            "border": 1, "border_color": c_border,
            "num_format": '"Rp" #,##0', "align": "right", "valign": "vcenter"
        })

        # ==========================================
        # SHEET 1: DETAIL TRANSAKSI
        # ==========================================
        sheet1 = workbook.add_worksheet(_("Detail Transaksi"))
        sheet1.hide_gridlines(2)
        sheet1.freeze_panes(6, 0)

        headers = [
            _("NO."),
            _("Reference"),
            _("Member No."),
            _("Member"),
            _("Member Type"),
            _("Borrow Date"),
            _("Due Date"),
            _("Status"),
            _("Books"),
            _("Book Details"),
            _("Total Fine"),
        ]
        last_column = len(headers) - 1

        sheet1.merge_range(0, 0, 0, last_column, _("Access to Library Management Tables"), title_format)
        sheet1.set_row(0, 32)

        sheet1.set_row(2, 20)
        sheet1.write(2, 0, _("From Date:"), meta_label_format)
        sheet1.write(2, 1, self.date_from, meta_val_date)
        sheet1.write(2, 3, _("To Date:"), meta_label_format)
        sheet1.write(2, 4, self.date_to, meta_val_date)
        sheet1.write(2, 6, _("Status:"), meta_label_format)
        sheet1.write(2, 7, dict(self._fields["state"].selection).get(self.state, _("All Confirmed")), meta_val_text)

        header_row = 5
        sheet1.set_row(header_row, 30)
        for column, header in enumerate(headers):
            sheet1.write(header_row, column, header, header_format)

        first_data_row = header_row + 1
        row = first_data_row
        member_types = dict(self.env["library.member"]._fields["member_type"].selection)
        loan_states = dict(self.env["library.loan"]._fields["state"].selection)

        for idx, loan in enumerate(loans, 1):
            is_overdue = bool(loan.is_overdue)
            is_even = (idx % 2 == 0)

            if is_overdue:
                c_center = cell_c_overdue
                c_left = cell_l_overdue
                c_wrap = wrap_l_overdue
                c_date = date_overdue
                c_money = money_overdue
            elif is_even:
                c_center = cell_c_pink
                c_left = cell_l_pink
                c_wrap = wrap_l_pink
                c_date = date_pink
                c_money = money_pink
            else:
                c_center = cell_c_white
                c_left = cell_l_white
                c_wrap = wrap_l_white
                c_date = date_white
                c_money = money_white

            status_display = loan_states.get(loan.state)
            if is_overdue:
                status_display = f"{status_display} (Overdue)"

            books = "\n".join(
                "%s%s" % (
                    line.book_id.name,
                    " (%s)" % line.isbn if line.isbn else "",
                )
                for line in loan.loan_line_ids
            )

            values = [
                (idx, c_center),
                (loan.name, c_center),
                (loan.member_id.member_number, c_center),
                (loan.member_id.name, c_left),
                (member_types.get(loan.member_id.member_type), c_center),
                (loan.date_borrow, c_date),
                (loan.date_return_expected, c_date),
                (status_display, c_center),
                (loan.book_count, c_center),
                (books, c_wrap),
                (loan.total_late_fee, c_money),
            ]

            for column, (value, style) in enumerate(values):
                sheet1.write(row, column, "" if value is None or value is False else value, style)

            line_count = max(1, books.count("\n") + 1)
            sheet1.set_row(row, max(22, 16 * line_count))
            row += 1

        last_data_row = row - 1
        sheet1.autofilter(header_row, 0, last_data_row, last_column)

        sheet1.set_column(0, 0, 7)    # NO.
        sheet1.set_column(1, 1, 16)   # Reference
        sheet1.set_column(2, 2, 14)   # Member No.
        sheet1.set_column(3, 3, 24)   # Member
        sheet1.set_column(4, 4, 14)   # Member Type
        sheet1.set_column(5, 6, 13)   # Dates
        sheet1.set_column(7, 7, 18)   # Status
        sheet1.set_column(8, 8, 8)    # Books
        sheet1.set_column(9, 9, 38)   # Book Details
        sheet1.set_column(10, 10, 16) # Total Fine

        r_start = first_data_row + 1
        r_end = last_data_row + 1

        summary_row = row + 1
        sheet1.set_row(summary_row, 24)
        sheet1.write(summary_row, 0, _("SUMMARY"), summary_title_format)
        sheet1.write(summary_row, 1, _("Total Loans"), summary_label_format)
        sheet1.write_formula(summary_row, 2, f'=COUNTA(B{r_start}:B{r_end})', summary_value_format, value=len(loans))
        sheet1.write(summary_row, 3, _("Ongoing"), summary_label_format)
        sheet1.write_formula(
            summary_row, 4,
            f'=COUNTIF(H{r_start}:H{r_end}, "*Ongoing*")',
            summary_value_format,
            value=len(loans.filtered(lambda l: l.state == "ongoing"))
        )
        sheet1.write(summary_row, 5, _("Returned"), summary_label_format)
        sheet1.write_formula(
            summary_row, 6,
            f'=COUNTIF(H{r_start}:H{r_end}, "*Returned*")',
            summary_value_format,
            value=len(loans.filtered(lambda l: l.state == "returned"))
        )
        sheet1.write(summary_row, 8, _("Total Fine"), summary_label_format)
        sheet1.write_formula(
            summary_row, 9,
            f'=SUM(K{r_start}:K{r_end})',
            summary_money_format,
            value=sum(loans.mapped("total_late_fee"))
        )

        # ==========================================
        # SHEET 2: REKAP RINGKAS & ANALISIS
        # ==========================================
        sheet2 = workbook.add_worksheet(_("Rekap & Analisis"))
        sheet2.hide_gridlines(2)

        sheet2.merge_range("A1:G1", _("Library Operations Analytics & Summary"), title_format)
        sheet2.set_row(0, 32)

        section_header_format = workbook.add_format({
            "bold": True,
            "font_name": "Segoe UI",
            "font_size": 11,
            "font_color": c_crimson,
            "bottom": 2,
            "bottom_color": c_crimson,
        })
        num_c_white = workbook.add_format({
            "font_name": "Segoe UI", "font_size": 9.5, "border": 1,
            "border_color": c_border, "bg_color": c_white,
            "valign": "vcenter", "align": "center", "num_format": "#,##0"
        })
        num_c_pink = workbook.add_format({
            "font_name": "Segoe UI", "font_size": 9.5, "border": 1,
            "border_color": c_border, "bg_color": c_pink_zebra,
            "valign": "vcenter", "align": "center", "num_format": "#,##0"
        })

        dash = self.env["library.dashboard"]

        # --- Table 1: Top 5 Buku Terfavorit ---
        sheet2.write("A3", _("Top 5 Buku Terfavorit"), section_header_format)
        sheet2.write("A4", _("Peringkat"), header_format)
        sheet2.write("B4", _("Judul Buku"), header_format)
        sheet2.write("C4", _("Total Dipinjam"), header_format)

        popular_books = dash.get_popular_books_data()[:5]
        for i, item in enumerate(popular_books, 1):
            r = 4 + i - 1
            c_bg = cell_c_pink if i % 2 == 0 else cell_c_white
            l_bg = cell_l_pink if i % 2 == 0 else cell_l_white
            n_bg = num_c_pink if i % 2 == 0 else num_c_white
            sheet2.write(r, 0, f"#{i}", c_bg)
            sheet2.write(r, 1, item.get("book") or "-", l_bg)
            sheet2.write(r, 2, item.get("count", 0), n_bg)
            sheet2.set_row(r, 20)

        # --- Table 2: Top 5 Anggota Paling Aktif ---
        sheet2.write("E3", _("Top 5 Anggota Teraktif"), section_header_format)
        sheet2.write("E4", _("Peringkat"), header_format)
        sheet2.write("F4", _("Nama Anggota"), header_format)
        sheet2.write("G4", _("Total Pinjaman"), header_format)

        top_members = dash.get_top_members_data()[:5]
        for i, item in enumerate(top_members, 1):
            r = 4 + i - 1
            c_bg = cell_c_pink if i % 2 == 0 else cell_c_white
            l_bg = cell_l_pink if i % 2 == 0 else cell_l_white
            n_bg = num_c_pink if i % 2 == 0 else num_c_white
            sheet2.write(r, 4, f"#{i}", c_bg)
            sheet2.write(r, 5, item.get("member") or "-", l_bg)
            sheet2.write(r, 6, item.get("loan_count", 0), n_bg)
            sheet2.set_row(r, 20)

        # --- Table 3: Statistik Berdasarkan Tipe Member ---
        start_t3 = 11
        sheet2.write(start_t3, 0, _("Statistik Peminjaman per Kategori Member"), section_header_format)
        sheet2.write(start_t3 + 1, 0, _("Tipe Anggota"), header_format)
        sheet2.write(start_t3 + 1, 1, _("Jumlah Anggota"), header_format)
        sheet2.write(start_t3 + 1, 2, _("Total Transaksi"), header_format)

        cat_stats = dash.get_category_stats()
        for idx, item in enumerate(cat_stats, 1):
            r = start_t3 + 1 + idx
            c_bg = cell_c_pink if idx % 2 == 0 else cell_c_white
            n_bg = num_c_pink if idx % 2 == 0 else num_c_white
            sheet2.write(r, 0, item.get("type") or "-", c_bg)
            sheet2.write(r, 1, item.get("member_count", 0), n_bg)
            sheet2.write(r, 2, item.get("loan_count", 0), n_bg)
            sheet2.set_row(r, 20)

        # Column widths for Sheet 2
        sheet2.set_column(0, 0, 14)  # Col A
        sheet2.set_column(1, 1, 32)  # Col B (Judul Buku)
        sheet2.set_column(2, 2, 16)  # Col C (Count)
        sheet2.set_column(3, 3, 5)   # Col D (Spacer)
        sheet2.set_column(4, 4, 14)  # Col E
        sheet2.set_column(5, 5, 28)  # Col F (Nama Anggota)
        sheet2.set_column(6, 6, 16)  # Col G (Count)

        workbook.close()
        attachment = self.env["ir.attachment"].create({
            "name": "Library_Loan_Report.xlsx",
            "type": "binary",
            "datas": base64.b64encode(output.getvalue()),
            "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "res_model": self._name,
            "res_id": self.id,
        })
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % attachment.id,
            "target": "self",
        }
