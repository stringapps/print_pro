"""Scheduled cleanup for Print Pro logs"""
import frappe
from frappe.utils import add_days, today


def clean_old_print_logs():
    """Delete print logs older than the configured retention period"""
    retention_days = frappe.db.get_single_value("Print Pro Settings", "print_log_retention_days") or 30
    cutoff_date = add_days(today(), -int(retention_days))
    old_logs = frappe.get_all(
        "Print Pro Log",
        filters={"printed_on": ["<", cutoff_date]},
        fields=["name"],
        limit=500,
    )
    for log in old_logs:
        frappe.delete_doc("Print Pro Log", log.name, ignore_permissions=True)
    if old_logs:
        frappe.db.commit()
        frappe.logger().info(f"Print Pro: Cleaned {len(old_logs)} old print logs.")
