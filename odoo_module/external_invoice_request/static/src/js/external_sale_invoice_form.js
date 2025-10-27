/** @odoo-module **/

import { Component, mount, useState, onWillStart } from "@odoo/owl";
import { jsonrpc } from "@web/core/network/rpc_service";

class ExternalSaleInvoiceForm extends Component {
    setup() {
        this.state = useState({
            loading: true,
            partner: null,
            sale_orders: [],
            selectedSale: null,
            message: "",
            invoices: [],
        });

        // Extract token from URL
        const pathParts = window.location.pathname.split("/");
        this.token = pathParts[pathParts.length - 1];

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        this.state.loading = true;
        try {
            // Get sale orders that can be invoiced
            const response = await fetch(`/external/sale-invoice/${this.token}`);
            const data = await response.json();
            this.state.partner = data.partner;
            this.state.sale_orders = data.sale_orders || [];

            // Get current invoice status
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

        this.state.message = "Submitting request";
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
        const url = `/external/download_invoice/${this.token}/${inv.invoice_id}`;
        window.open(url, "_blank");
    }
}

ExternalSaleInvoiceForm.template = "external_invoice_request.ExternalSaleInvoiceForm";

export default ExternalSaleInvoiceForm;

mount(ExternalSaleInvoiceForm, document.getElementById("external_sale_invoice"));



import { xml } from "@odoo/owl";

ExternalSaleInvoiceForm.template = xml/* xml */ `
  <div t-if="state.loading">Loading...</div>
  <div t-else="">
    <div class="card p-4 shadow-sm">
      <h4>Partner: <t t-esc="state.partner"/></h4>

      <div class="mt-3">
        <label>Sale Orders:</label>
        <select t-model="state.selectedSale" class="form-select">
          <option value="">-- Select Sale Order --</option>
          <t t-foreach="state.sale_orders" t-as="so" t-key="so.id">
            <option t-att-value="so.id"><t t-esc="so.name"/> — $<t t-esc="so.amount_total"/></option>
          </t>
        </select>
      </div>

      <button t-on-click="requestInvoice" class="btn btn-primary mt-3">Request Invoice</button>
      <p class="mt-3 text-info"><t t-esc="state.message"/></p>
    </div>

    <div class="mt-5">
      <h5>Invoice Requests</h5>
      <table class="table table-striped mt-2">
        <thead>
          <tr>
            <th>Sale Order</th>
            <th>Status</th>
            <th>Invoice</th>
          </tr>
        </thead>
        <tbody>
          <t t-foreach="state.invoices" t-as="inv" t-key="inv.sale_order">
            <tr>
              <td><t t-esc="inv.sale_order"/></td>
              <td><t t-esc="inv.status"/></td>
              <td>
                <t t-if="inv.invoice_id">
                  <button t-on-click="() => downloadInvoice(inv)" class="btn btn-success btn-sm">
                    Download PDF
                  </button>
                </t>
                <t t-else="">—</t>
              </td>
            </tr>
          </t>
        </tbody>
      </table>
    </div>
  </div>
`;
