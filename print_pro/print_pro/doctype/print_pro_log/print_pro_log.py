"""Print Pro Log - Audit trail for all print actions"""
import frappe
from frappe.model.document import Document


class PrintProLog(Document):
    pass


def create_log(document_type, document_name, status, printer=None, print_format=None,
               copies=1, paper_size=None, orientation=None, error=None):
    """Helper to create a print log entry"""
    try:
        log = frappe.new_doc("Print Pro Log")
        log.document_type = document_type
        log.document_name = document_name
        log.status = status
        log.printer = printer
        log.print_format = print_format
        log.copies = copies
        log.paper_size = paper_size
        log.orientation = orientation
        log.printed_by = frappe.session.user
        log.printed_on = frappe.utils.now_datetime()
        log.error_message = error
        log.insert(ignore_permissions=True)
        frappe.db.commit()
        return log.name
    except Exception:
        pass
