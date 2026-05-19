"""Auto-print hook on document submit"""
import frappe


def on_submit_auto_print(doc, method=None):
    """Triggered on every doc submit — auto prints if configured"""
    try:
        settings = frappe.get_single("Print Pro Settings")
        if not settings.enabled or not settings.auto_print_on_submit:
            return

        fmt = frappe.get_value(
            "Print Pro Format",
            {"document_type": doc.doctype, "is_default": 1, "enabled": 1},
            "name",
        )
        if not fmt:
            return

        from print_pro.utils.print_engine import execute_print
        execute_print(
            doctype=doc.doctype,
            docname=doc.name,
            format_name=fmt,
        )
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Print Pro - Auto Print Failed")
