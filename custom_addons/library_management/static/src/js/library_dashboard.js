/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, onWillUnmount, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class LibraryDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            data: null,
            loading: true,
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });

        onMounted(() => {
            this.refreshInterval = setInterval(() => {
                this.loadDashboardData();
            }, 300000);
        });

        onWillUnmount(() => {
            if (this.refreshInterval) {
                clearInterval(this.refreshInterval);
            }
        });
    }

    async loadDashboardData() {
        try {
            this.state.loading = true;
            const dashboardIds = await this.orm.search("library.dashboard", [], { limit: 1 });
            if (dashboardIds.length > 0) {
                const data = await this.orm.call(
                    "library.dashboard",
                    "get_dashboard_data",
                    [dashboardIds[0]]
                );
                this.state.data = data;
            }
            this.state.loading = false;
        } catch (error) {
            console.error("Dashboard load error:", error);
            this.state.loading = false;
        }
    }

    async onRefresh() {
        await this.loadDashboardData();
    }

    // Format currency
    formatCurrency(value) {
        if (!value) return "Rp 0";
        return "Rp " + Math.round(value).toLocaleString("id-ID");
    }

    // Chart helper: max value for bar scaling
    getChartMax(items) {
        if (!items || !items.length) return 1;
        const max = Math.max(...items.map(i => i.count));
        return max || 1;
    }

    getBarHeight(count, max) {
        if (!max) return 0;
        return Math.round((count / max) * 100);
    }

    // Helpers for template (OWL templates can't call .map inline)
    getCategoryChartMax() {
        const stats = this.state.data && this.state.data.category_stats;
        if (!stats || !stats.length) return 1;
        return Math.max(...stats.map(c => c.loan_count)) || 1;
    }

    getMemberChartMax() {
        const members = this.state.data && this.state.data.top_members;
        if (!members || !members.length) return 1;
        return Math.max(...members.map(m => m.loan_count)) || 1;
    }

    getLoanTrendMax() {
        const trends = this.state.data && this.state.data.loan_trends;
        if (!trends || !trends.length) return 1;
        return Math.max(...trends.map(i => i.count)) || 1;
    }

    getPopularBooksMax() {
        const books = this.state.data && this.state.data.popular_books;
        if (!books || !books.length) return 1;
        return Math.max(...books.map(b => b.count)) || 1;
    }

    // Badge class by state
    getStateBadge(state) {
        const map = {
            'draft': 'bg-secondary',
            'ongoing': 'bg-primary',
            'returned': 'bg-success',
        };
        return map[state] || 'bg-secondary';
    }

    getStateLabel(state) {
        const map = {
            'draft': 'Draft',
            'ongoing': 'Dipinjam',
            'returned': 'Dikembalikan',
        };
        return map[state] || state;
    }

    // Severity class for overdue days
    getOverdueSeverity(days) {
        if (days > 14) return 'text-danger fw-bold';
        if (days > 7) return 'text-warning fw-bold';
        return 'text-dark';
    }

    // Navigation actions
    openBooks() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Semua Buku',
            res_model: 'library.book',
            views: [[false, 'kanban'], [false, 'list'], [false, 'form']],
            domain: [['active', '=', true]],
        });
    }

    openMembers() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Semua Anggota',
            res_model: 'library.member',
            views: [[false, 'list'], [false, 'form']],
        });
    }

    openActiveLoans() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Pinjaman Aktif',
            res_model: 'library.loan',
            views: [[false, 'list'], [false, 'form']],
            domain: [['state', '=', 'ongoing']],
        });
    }

    openOverdueLoans() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Pinjaman Terlambat',
            res_model: 'library.loan',
            views: [[false, 'list'], [false, 'form']],
            domain: [['state', '=', 'ongoing'], ['date_return_expected', '<', new Date().toISOString().split('T')[0]]],
            context: { create: false },
        });
    }

    openAllLoans() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Semua Pinjaman',
            res_model: 'library.loan',
            views: [[false, 'list'], [false, 'form']],
        });
    }

    openLoanDetail(loanId) {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Detail Pinjaman',
            res_model: 'library.loan',
            views: [[false, 'form']],
            res_id: loanId,
        });
    }

    openLoanAnalysis() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Analisis Pinjaman',
            res_model: 'library.loan',
            views: [[false, 'graph'], [false, 'pivot'], [false, 'list']],
            context: { group_by: ['date_borrow'] },
        });
    }

    openPopularBooks() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Buku Populer',
            res_model: 'library.loan.line',
            views: [[false, 'graph'], [false, 'pivot'], [false, 'list']],
            context: { group_by: ['book_id'] },
        });
    }
}

LibraryDashboard.template = "library_management.LibraryDashboard";

registry.category("actions").add("library_dashboard", LibraryDashboard);
