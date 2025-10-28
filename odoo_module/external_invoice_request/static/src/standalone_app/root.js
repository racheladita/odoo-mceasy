/** @odoo-module **/
import { Component, mount, useState, onWillStart } from "@odoo/owl";
import { jsonrpc } from "@web/core/network/rpc_service";

export class ExternalSaleInvoiceForm extends Component {
    setup() {
        this.state = useState({
            loading: true,
            partner: null,
            sale_orders: [],
            selectedSale: null,
            message: "",
            invoices: [],
        });

        const pathParts = window.location.pathname.split("/");
        this.token = pathParts[pathParts.length - 1];

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        this.state.loading = true;
        try {
            const response = await fetch(`/external/sale-invoice/${this.token}`);
            const data = await response.json();
            this.state.partner = data.partner;
            this.state.sale_orders = data.sale_orders || [];

            const statusResponse = await fetch(`/external/invoice-status/${this.token}`);
            const statusData = await statusResponse.json();
            this.state.invoices = statusData.invoice_requests || [];
        } catch (error) {
            this.state.message = "Failed to load data.";
            console.error(error);
        }
        this.state.loading = false;
    }

    async requestInvoice() {
        if (!this.state.selectedSale) {
            this.state.message = "Please select a Sale Order first.";
            return;
        }
        this.state.message = "Submitting request...";
        try {
            const res = await jsonrpc("/external/request_invoice", {
                token: this.token,
                sale_order_id: this.state.selectedSale,
            });
            this.state.message = res.message;
            await this.loadData();
        } catch (error) {
            this.state.message = "Error submitting request.";
            console.error(error);
        }
    }

    downloadInvoice(inv) {
        const url = `/external/download-invoice/${this.token}/${inv.invoice_id}`;
        window.open(url, "_blank");
    }
}

ExternalSaleInvoiceForm.template = "external_invoice_request.ExternalSaleInvoiceForm";
