// static/src/js/dashboard.js
odoo.define('it_recruitment.dashboard', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;

    var RecruitmentDashboard = AbstractAction.extend({
        template: 'it_recruitment.dashboard',
        events: {
            'click button[name="action_open_applicants"]': '_onOpenApplicants',
            'click button[name="action_open_jobs"]': '_onOpenJobs',
        },

        init: function(parent, context) {
            this._super(parent, context);
            this.dashboard_data = {};
        },

        willStart: function() {
            var self = this;
            return this._super().then(function() {
                return self._loadDashboardData();
            });
        },

        _loadDashboardData: function() {
            var self = this;
            return this._rpc({
                model: 'it.recruitment.stats',
                method: 'search_read',
                args: [[]],
            }).then(function(result) {
                if (result.length > 0) {
                    self.dashboard_data = result[0];
                }
                return self._rpc({
                    model: 'it.recruitment.applicant',
                    method: 'search_read',
                    args: [[], ['name', 'email', 'job_id', 'current_round', 'final_status', 'application_date']],
                    kwargs: {limit: 5, order: 'create_date desc'}
                });
            }).then(function(recent_applicants) {
                self.recent_applicants = recent_applicants;
            });
        },

        start: function() {
            var self = this;
            return this._super().then(function() {
                self._renderCharts();
            });
        },

        _renderCharts: function() {
            // Round Distribution Chart
            var roundCtx = document.getElementById('round_chart').getContext('2d');
            var roundChart = new Chart(roundCtx, {
                type: 'bar',
                data: {
                    labels: ['Aptitude Test', 'Coding Round', 'HR Interview', 'Final Decision'],
                    datasets: [{
                        label: 'Applicants by Round',
                        data: [
                            this.dashboard_data.round_1_count,
                            this.dashboard_data.round_2_count,
                            this.dashboard_data.round_3_count,
                            this.dashboard_data.final_count
                        ],
                        backgroundColor: [
                            'rgba(255, 159, 64, 0.7)',
                            'rgba(255, 205, 86, 0.7)',
                            'rgba(54, 162, 235, 0.7)',
                            'rgba(153, 102, 255, 0.7)'
                        ],
                        borderColor: [
                            'rgba(255, 159, 64, 1)',
                            'rgba(255, 205, 86, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(153, 102, 255, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });

            // Status Distribution Chart
            var statusCtx = document.getElementById('status_chart').getContext('2d');
            var statusChart = new Chart(statusCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Hired', 'Rejected', 'Pending'],
                    datasets: [{
                        data: [
                            this.dashboard_data.hired_count,
                            this.dashboard_data.rejected_count,
                            this.dashboard_data.pending_count
                        ],
                        backgroundColor: [
                            'rgba(40, 167, 69, 0.7)',
                            'rgba(220, 53, 69, 0.7)',
                            'rgba(255, 193, 7, 0.7)'
                        ],
                        borderColor: [
                            'rgba(40, 167, 69, 1)',
                            'rgba(220, 53, 69, 1)',
                            'rgba(255, 193, 7, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                        }
                    }
                }
            });
        },

        _onOpenApplicants: function() {
            this.do_action({
                type: 'ir.actions.act_window',
                name: 'Applicants',
                res_model: 'it.recruitment.applicant',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                target: 'current'
            });
        },

        _onOpenJobs: function() {
            this.do_action({
                type: 'ir.actions.act_window',
                name: 'Job Positions',
                res_model: 'it.recruitment.job',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                target: 'current'
            });
        },
    });

    core.action_registry.add('it_recruitment.dashboard', RecruitmentDashboard);

    return {
        RecruitmentDashboard: RecruitmentDashboard,
    };
});