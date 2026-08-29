/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class LibraryDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            data: {},
            loading: true,
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });

        onMounted(() => {
            // Auto-refresh every 5 minutes (300000 ms)
            this.refreshInterval = setInterval(() => {
                this.loadDashboardData();
            }, 300000);
        });

        // Cleanup interval on component destroy
        onWillUnmount(() => {
            if (this.refreshInterval) {
                clearInterval(this.refreshInterval);
            }
        });
    }

    async loadDashboardData() {
        try {
            this.state.loading = true;
            
            // Get the dashboard singleton record
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
            console.error("Error loading dashboard data:", error);
            this.state.loading = false;
        }
    }

    onClickKPI(kpiType) {
        // Handle KPI card clicks to open filtered views
        let action = {};
        
        switch(kpiType) {
            case 'books':
                action = {
                    type: 'ir.actions.act_window',
                    name: 'Books',
                    res_model: 'library.book',
                    view_mode: 'kanban,list,form',
                    domain: [['active', '=', true]],
                };
                break;
            case 'members':
                action = {
                    type: 'ir.actions.act_window',
                    name: 'Members',
                    res_model: 'library.member',
                    view_mode: 'list,form',
                };
                break;
            case 'active_loans':
                action = {
                    type: 'ir.actions.act_window',
                    name: 'Active Loans',
                    res_model: 'library.loan',
                    view_mode: 'list,form',
                    domain: [['state', '=', 'ongoing']],
                };
                break;
            case 'overdue_loans':
                action = {
                    type: 'ir.actions.act_window',
                    name: 'Overdue Loans',
                    res_model: 'library.loan',
                    view_mode: 'list,form',
                    domain: [['state', '=', 'ongoing'], ['date_return_expected', '<', new Date().toISOString().split('T')[0]]],
                };
                break;
        }
        
        if (action.type) {
            this.action.doAction(action);
        }
    }
}

LibraryDashboard.template = "library_management.LibraryDashboard";

registry.category("actions").add("library_dashboard", LibraryDashboard);
