"""Print Pro - Installation & Migration hooks"""
import frappe


def after_install():
    create_default_settings()
    create_default_printers()
    frappe.db.commit()
    frappe.msgprint(
        """<b>Print Pro installed successfully!</b><br><br>
        <b>IMPORTANT — Run these commands on your server to activate the UI:</b><br>
        <code>bench build --app print_pro</code><br>
        <code>bench --site {site} clear-cache</code><br><br>
        Then go to <b>Print Pro Settings</b> to configure.<br>
        The <b>🖨 Print Pro</b> button will appear on all supported documents under the <b>Print</b> menu.
        """.format(site=frappe.local.site),
        title="Print Pro Installed ✓",
        indicator="green",
    )


def after_migrate():
    create_default_settings()
    _sync_workspace()


def create_default_settings():
    if not frappe.db.exists("Print Pro Settings", "Print Pro Settings"):
        doc = frappe.new_doc("Print Pro Settings")
        doc.enabled = 1
        doc.default_paper_size = "A4"
        doc.default_orientation = "Portrait"
        doc.show_print_pro_button = 1
        doc.replace_default_print = 0
        doc.print_log_retention_days = 30
        doc.show_print_preview = 1
        doc.watermark_on_draft = 1
        doc.watermark_text = "DRAFT"
        doc.insert(ignore_permissions=True)


def create_default_printers():
    if not frappe.db.count("Print Pro Printer"):
        doc = frappe.new_doc("Print Pro Printer")
        doc.printer_name = "Default Printer"
        doc.printer_type = "PDF"
        doc.is_default = 1
        doc.paper_size = "A4"
        doc.orientation = "Portrait"
        doc.copies = 1
        doc.enabled = 1
        doc.insert(ignore_permissions=True)


def _sync_workspace():
    """Ensure workspace is loaded from JSON if not already in DB"""
    try:
        if not frappe.db.exists("Workspace", "Print Pro"):
            frappe.reload_doc("print_pro", "workspace", "Print Pro")
    except Exception:
        pass
