from . import __version__ as app_version

app_name = "print_pro"
app_title = "Print Pro"
app_publisher = "Print Pro"
app_description = "Advanced Printing Solution for ERPNext v15 - Direct print, custom formats, multi-printer support"
app_email = "support@printpro.io"
app_license = "MIT"
app_version = app_version

# ─── Required Apps ────────────────────────────────────────────────────────────
required_apps = ["frappe", "erpnext"]

# ─── App includes (loaded on EVERY Frappe page after bench build) ─────────────
# Run:  bench build --app print_pro  &&  bench --site <site> clear-cache
app_include_css = [
    "/assets/print_pro/css/print_pro.css",
]
app_include_js = [
    "/assets/print_pro/js/print_pro.js",
]

# ─── Doctype JS overrides ─────────────────────────────────────────────────────
# These files are served by Frappe DIRECTLY — no bench build required.
# Each file is self-contained: button always appears, full dialog loads on-demand.
doctype_js = {
    # ── Selling ──────────────────────────────────────────────────────────────
    "Sales Invoice":        "public/js/overrides/sales_invoice.js",
    "Quotation":            "public/js/overrides/quotation.js",
    "Sales Order":          "public/js/overrides/sales_order.js",
    "Delivery Note":        "public/js/overrides/delivery_note.js",
    "Sales Return":         "public/js/overrides/sales_return.js",
    # ── Buying ───────────────────────────────────────────────────────────────
    "Purchase Invoice":     "public/js/overrides/purchase_invoice.js",
    "Purchase Order":       "public/js/overrides/purchase_order.js",
    "Purchase Receipt":     "public/js/overrides/purchase_receipt.js",
    "Supplier Quotation":   "public/js/overrides/supplier_quotation.js",
    # ── Stock ────────────────────────────────────────────────────────────────
    "Stock Entry":          "public/js/overrides/stock_entry.js",
    "Material Request":     "public/js/overrides/material_request.js",
    "Delivery Trip":        "public/js/overrides/delivery_trip.js",
    "Stock Reconciliation": "public/js/overrides/stock_reconciliation.js",
    "Packing Slip":         "public/js/overrides/packing_slip.js",
    # ── Accounts ─────────────────────────────────────────────────────────────
    "Payment Entry":        "public/js/overrides/payment_entry.js",
    "Journal Entry":        "public/js/overrides/journal_entry.js",
    "Expense Claim":        "public/js/overrides/expense_claim.js",
    # ── HR / Payroll ─────────────────────────────────────────────────────────
    "Salary Slip":          "public/js/overrides/salary_slip.js",
    "Leave Application":    "public/js/overrides/leave_application.js",
    # ── Manufacturing ────────────────────────────────────────────────────────
    "Work Order":           "public/js/overrides/work_order.js",
    "Job Card":             "public/js/overrides/job_card.js",
    "BOM":                  "public/js/overrides/bom.js",
    # ── Print Pro own DocTypes ───────────────────────────────────────────────
    "Print Pro Printer":    "public/js/overrides/print_pro_printer.js",
}

# ─── Fixtures (exported/imported during bench migrate) ────────────────────────
fixtures = [
    {
        "dt": "Workspace",
        "filters": [["name", "=", "Print Pro"]],
    },
    {
        "dt": "Print Pro Format",
        "filters": [["enabled", "=", 1]],
    },
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "Print Pro"]],
    },
]

# ─── Scheduled Tasks ──────────────────────────────────────────────────────────
scheduler_events = {
    "daily": [
        "print_pro.utils.cleanup.clean_old_print_logs",
    ],
}

# ─── Permission hooks ─────────────────────────────────────────────────────────
has_permission = {
    "Print Pro Printer": "print_pro.print_pro.doctype.print_pro_printer.print_pro_printer.has_permission",
    "Print Pro Format":  "print_pro.print_pro.doctype.print_pro_format.print_pro_format.has_permission",
}

# ─── Doc events ───────────────────────────────────────────────────────────────
doc_events = {
    "*": {
        "on_submit": "print_pro.utils.auto_print.on_submit_auto_print",
    }
}

# ─── Boot session (injects settings into frappe.boot for JS access) ───────────
boot_session = "print_pro.utils.boot.boot_session"

# ─── Installation hooks ───────────────────────────────────────────────────────
after_install = "print_pro.install.after_install"
after_migrate = "print_pro.install.after_migrate"
