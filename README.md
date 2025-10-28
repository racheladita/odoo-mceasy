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

---

## Client Backend

The client backend runs separately (default port 5000). It allows user to :
1. Creating SO via API.
2. Update SO via API.
3. Get list SO via API.
4. Get SO detail via API.
5. Confirm SO via API.
6. Cancel SO via API.
7. Reset SO (set to draft) via API.

Accessible at http://localhost:5000

---

## Odoo Endpoints

1. Get Partner Sale Orders
   URL
   ```bash
   GET http://localhost:8069/external/sale-invoice/d937872e-81aa-4f4a-adf5-501928f32e1d
   ```
   Response Example:
   ```bash
   {
    "partner": "Brandon Freeman",
    "sale_orders": [
      {
        "id": 21,
        "name": "S00021",
        "amount_total": 99.9,
        "date_order": "2025-10-27 10:58:16"
      }
    ]
   }
   ```
   
2. Request Invoice
   URL
   ```bash
   POST http://localhost:8069/external/request-invoice
   ```
   Headers:
   ```bash
   Content-Type: application/json
   ```
   Payload Example:
   ```bash
   {
      "token": "<partner_token>",
      "sale_order_id": 21
   }
   ```
   Response Example:
   ```bash
   {
      "status": "pending",
      "message": "Invoice request created successfully. Awaiting approval."
   }
   ```

3. Get Invoice Status
   URL
   ```bash
   GET http://localhost:8069/external/invoice-status/d937872e-81aa-4f4a-adf5-501928f32e1d
   ```
   Response Example:
   ```bash
   {
      "partner": "Brandon Freeman",
      "invoice_requests": [
        {
          "sale_order": "S00021",
          "status": "approved",
          "invoice_id": 10,
          "invoice_name": "INV/2025/10"
        }
      ]
   }
   ```

4. Download Invoice PDF
   URL
   ```bash
   GET http://localhost:8069/external/download-invoice/d937872e-81aa-4f4a-adf5-501928f32e1d/49
   ```
   Returns a PDF file for download

---

## Client Backend Endpoint

1. Create Sales Order
   URL
   ```bash
   POST http://localhost:5000/so/create
   ```
   Headers:
   ```bash
   Content-Type: application/json
   ```
   Payload Example:
   ```bash
   {
      "partner_id": 4,
      "order_lines": [
        {
          "product_id": 1,
          "qty": 1,
          "price_unit": 100
        }
      ]
   }
   ```
   Response Example:
   ```bash
   {
      "success": true,
      "sale_order_id": 21
   }
   ```

Testing via Postman :
1. Open Postman.
2. Select the method (GET or POST).
3. Enter URL with the correct IDs.
4. For POST, select Body → raw → JSON and paste payload.
5. Send request → check response.

---

## Docker Compose File
```bash
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
    volumes:
      - odoo-db-data:/var/lib/postgresql/data

  odoo:
    image: odoo:17
    depends_on:
      - db
    ports:
      - "8069:8069"
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
    volumes:
      - ./odoo_module:/mnt/extra-addons

  client_app:
    build: ./client_app
    depends_on:
      - odoo
    environment:
      - ODOO_URL=http://odoo:8069
      - ODOO_DB=mceasy
      - ODOO_USER=odoo
      - ODOO_PASS=odoo
    ports:
      - "5000:5000"

volumes:
  odoo-db-data:
```

---

## Screenshot of the Program

1. OWL External Invoice Request (without login to Odoo)
<img width="1122" height="759" alt="Screenshot 2025-10-28 at 07 53 09" src="https://github.com/user-attachments/assets/d6fea6a9-3941-4a79-b8f0-267eb8134371" />
<img width="1124" height="760" alt="Screenshot 2025-10-28 at 08 01 39" src="https://github.com/user-attachments/assets/02045c3e-1d4e-41c9-b8d6-e531bb80bf82" />
<img width="1124" height="762" alt="Screenshot 2025-10-28 at 08 01 58" src="https://github.com/user-attachments/assets/901dbf1f-fcec-4429-a42f-a1e97e32bf17" />
<img width="1123" height="764" alt="Screenshot 2025-10-28 at 08 02 21" src="https://github.com/user-attachments/assets/0482bd39-0bc0-4291-b4a5-076a12c461da" />
<img width="1123" height="761" alt="Screenshot 2025-10-28 at 08 19 25" src="https://github.com/user-attachments/assets/fe32eda0-d925-43ca-91fa-593099061252" />

2. Client Backend
   1. Create Sales Order
      <img width="1124" height="765" alt="Screenshot 2025-10-28 at 08 03 56" src="https://github.com/user-attachments/assets/fd226605-28f5-4162-835c-1f0b584b969e" />
   2. Update Sales Order
      <img width="1125" height="767" alt="Screenshot 2025-10-28 at 08 05 41" src="https://github.com/user-attachments/assets/551d87da-3c84-4248-8ce3-d48d543bcb79" />
   3. Get list Sales Order
      <img width="1122" height="764" alt="Screenshot 2025-10-28 at 08 06 57" src="https://github.com/user-attachments/assets/4673fecf-f667-4f5d-bfe0-db4afdd12bd0" />
   4. Get Sales Order detail
      <img width="1122" height="761" alt="Screenshot 2025-10-28 at 08 09 39" src="https://github.com/user-attachments/assets/c73d5217-3e70-4b7c-901b-fd7bf0e07d8e" />
   5. Confirm Sales Order
      <img width="1123" height="761" alt="Screenshot 2025-10-28 at 08 11 33" src="https://github.com/user-attachments/assets/892ae092-7309-4fe0-8e3a-6165fb4207de" />
   6. Cancel Sales Order
      <img width="1120" height="753" alt="Screenshot 2025-10-28 at 08 13 40" src="https://github.com/user-attachments/assets/8d5004fa-4215-4221-9e87-2277924e4d0d" />
   7. Reset Sales Order (set to draft)
      <img width="1121" height="760" alt="Screenshot 2025-10-28 at 08 15 31" src="https://github.com/user-attachments/assets/1745b233-4c42-42ee-9ce9-b9b5e05f1361" />

