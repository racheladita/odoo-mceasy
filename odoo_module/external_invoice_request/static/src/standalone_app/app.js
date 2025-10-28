/** @odoo-module **/
import { whenReady } from "@odoo/owl";
import { mountComponent } from "@web/env";
import { ExternalSaleInvoiceForm } from "./root";

whenReady(() => mountComponent(ExternalSaleInvoiceForm, document.getElementById("external_sale_invoice")));