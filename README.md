# 🖨️ Print Pro — ERPNext v15

> **Advanced Printing Solution for ERPNext** — Direct print, custom formats, multi-printer support, and a professional print dialog that replaces (or enhances) the default ERPNext print flow.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🖨️ **Multi-Printer Support** | PDF, Network (IP/RAW), USB, Email, Cloud Print |
| 📄 **Custom Print Formats** | Create formats per DocType with custom HTML/CSS or based on ERPNext formats |
| 🎛️ **Print Pro Dialog** | Beautiful dialog with format selection, printer selection, paper size, copies |
| 🔁 **Print History** | Per-document print log with status tracking |
| ⚡ **Auto Print on Submit** | Automatically print when a document is submitted |
| 🔑 **Keyboard Shortcut** | `Ctrl+Shift+P` anywhere on a document |
| 🌊 **Watermark on Drafts** | Shows DRAFT watermark on unsaved/unsubmitted docs |
| 📧 **Email as PDF** | Print by emailing document as PDF attachment |
| 🔒 **Role-based Access** | Fine-grained permissions per printer and format |
| 📦 **ERPNext Compatible** | Works alongside or replaces the default print button |

---

## 📦 Installation (ERPNext v15)

```bash
# In your frappe-bench directory:
bench get-app print_pro https://github.com/yourusername/print_pro_v15.git

# Install on your site:
bench --site your-site.com install-app print_pro

# Migrate:
bench --site your-site.com migrate
```

---

## ⚙️ Configuration

1. Go to **Print Pro Settings** (search in awesome bar)
2. Enable Print Pro
3. Configure default paper size, orientation, and whether to **replace** or **supplement** the default print button

---

## 🖨️ Setting Up Printers

Go to **Print Pro Printer** and create printer entries:

| Type | Use Case |
|---|---|
| PDF | Download / save PDF locally |
| Network (IP) | Send RAW data to network printers (ESC/POS etc.) |
| USB | Direct USB thermal/receipt printers |
| Email | Print = send PDF via email |
| Cloud Print | Custom cloud integration |

---

## 📄 Creating Print Formats

Go to **Print Pro Format** and create a format:

- Select the **DocType** (Sales Invoice, Purchase Invoice, etc.)
- Choose a **base**: ERPNext's existing format, or write your own **Custom HTML**
- Add **Custom CSS**, **Header HTML**, **Footer HTML**
- Assign a default **Printer**
- Set as **default** for that DocType

---

## 📌 Supported DocTypes

| Module | DocTypes |
|---|---|
| Selling | Sales Invoice, Quotation, Sales Order, Delivery Note |
| Buying | Purchase Invoice, Purchase Order, Purchase Receipt, Supplier Quotation |
| Stock | Stock Entry, Material Request, Delivery Trip, Stock Reconciliation, Packing Slip |
| Accounts | Payment Entry, Journal Entry, Expense Claim |
| HR/Payroll | Salary Slip, Leave Application |
| Manufacturing | Work Order, Job Card, BOM |

---

## 🔑 Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+Shift+P` | Open Print Pro dialog for current document |
| `Ctrl+Enter` (in dialog) | Execute print immediately |

---

## 🗂️ Folder Structure

```
print_pro_v15/
├── print_pro/
│   ├── hooks.py                  # ERPNext v15 hooks
│   ├── install.py                # After-install setup
│   ├── api.py                    # All whitelisted API endpoints
│   ├── config/
│   │   └── desktop.py           # Module icon & workspace
│   ├── print_pro/
│   │   └── doctype/
│   │       ├── print_pro_settings/    # Global settings (singleton)
│   │       ├── print_pro_printer/     # Printer configurations
│   │       ├── print_pro_format/      # Custom print formats
│   │       ├── print_pro_log/         # Print audit log
│   │       ├── print_pro_printer_doctype/   # Child table
│   │       └── print_pro_format_condition/  # Child table
│   ├── utils/
│   │   ├── print_engine.py      # Core print dispatcher
│   │   ├── boot.py              # Boot session injection
│   │   ├── auto_print.py        # Auto-print on submit hook
│   │   └── cleanup.py           # Scheduled log cleanup
│   └── public/
│       ├── js/
│       │   ├── print_pro.js           # Core dialog controller
│       │   ├── print_pro.bundle.js    # Bundle entry
│       │   └── overrides/             # Per-doctype form JS (22 files)
│       └── css/
│           └── print_pro.css         # Professional UI styles
├── .github/workflows/ci.yml      # GitHub Actions CI
├── setup.py
├── requirements.txt
├── MANIFEST.in
└── README.md
```

---

## 📜 License

MIT — © Print Pro
