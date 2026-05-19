"""Print Pro Printer - Printer configuration DocType"""
import frappe
from frappe import _
from frappe.model.document import Document


class PrintProPrinter(Document):

    def validate(self):
        self._validate_network_printer()
        self._validate_usb_printer()
        self._set_single_default()

    def _validate_network_printer(self):
        if self.printer_type == "Network (IP)":
            if not self.printer_ip:
                frappe.throw(_("Printer IP Address is required for Network printers."))
            if not self.printer_port:
                self.printer_port = "9100"

    def _validate_usb_printer(self):
        if self.printer_type == "USB":
            if not self.usb_vendor_id or not self.usb_product_id:
                frappe.throw(_("USB Vendor ID and Product ID are required for USB printers."))

    def _set_single_default(self):
        """Only one printer can be default"""
        if self.is_default:
            frappe.db.set_value(
                "Print Pro Printer",
                {"is_default": 1, "name": ["!=", self.name]},
                "is_default",
                0,
            )

    def get_print_settings(self):
        """Return dict of print settings for this printer"""
        return {
            "printer_name": self.printer_name,
            "printer_type": self.printer_type,
            "paper_size": self.paper_size,
            "orientation": self.orientation,
            "copies": self.copies or 1,
            "margins": {
                "top": self.margin_top or 10,
                "right": self.margin_right or 10,
                "bottom": self.margin_bottom or 10,
                "left": self.margin_left or 10,
            },
        }


def has_permission(doc, user=None, ptype="read"):
    return frappe.has_permission("Print Pro Printer", ptype, doc, user=user)


@frappe.whitelist()
def get_default_printer():
    """Return the default printer"""
    printer = frappe.get_value(
        "Print Pro Printer", {"is_default": 1, "enabled": 1}, "name"
    )
    if printer:
        return frappe.get_doc("Print Pro Printer", printer).get_print_settings()
    return {}


@frappe.whitelist()
def get_printers_for_doctype(doctype):
    """Return list of enabled printers applicable for a doctype"""
    all_printers = frappe.get_all(
        "Print Pro Printer",
        filters={"enabled": 1},
        fields=["name", "printer_name", "printer_type", "is_default", "paper_size"],
    )
    result = []
    for p in all_printers:
        applicable = frappe.get_all(
            "Print Pro Printer Doctype",
            filters={"parent": p.name},
            fields=["document_type"],
        )
        applicable_list = [a.document_type for a in applicable]
        if not applicable_list or doctype in applicable_list:
            result.append(p)
    return result
