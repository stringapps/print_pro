"""Print Pro Settings - Singleton DocType"""
import frappe
from frappe.model.document import Document


class PrintProSettings(Document):
    def validate(self):
        if self.print_log_retention_days and self.print_log_retention_days < 1:
            frappe.throw("Print Log Retention Days must be at least 1.")

    def on_update(self):
        frappe.cache().delete_value("print_pro_settings")

    @staticmethod
    def get_settings():
        """Cached settings fetch"""
        settings = frappe.cache().get_value("print_pro_settings")
        if not settings:
            settings = frappe.get_single("Print Pro Settings")
            frappe.cache().set_value("print_pro_settings", settings)
        return settings
