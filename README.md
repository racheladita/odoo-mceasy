# OWL External Invoice Request Module & XML-RPC Client

This module allows external partners to request and download invoices through a public link without logging into Odoo. It also provides a simple client API for testing or creating Sales Orders.

---

## Prerequisites

- Docker & Docker Compose installed
- Odoo 17 (or compatible version)
- Modules to install in Odoo:  
  - Contacts  
  - Sales  
  - Accounting  
- Developer mode enabled in Odoo


## Features

- Public partner page showing sale orders ready to invoice
- Request invoice creation without Odoo login
- View invoice request status
- Download invoice PDF once approved
- Automatic invoice approval via cron (optional)
- Client API for manage Sales Order via JSON

---

## Run Odoo & Module

```bash
docker compose up --build
```


1. Open Odoo: http://localhost:8069
2. Create a new database.
3. Install Contacts, Sales, and Accounting modules.
4. Update Apps List and install OWL External Invoice Request.