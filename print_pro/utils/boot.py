"""Inject Print Pro settings into boot session"""
import frappe


def boot_session(bootinfo):
    """Add Print Pro config to boot session so JS can access it"""
    try:
        settings = frappe.get_single("Print Pro Settings")
        bootinfo.print_pro = {
            "enabled": settings.enabled,
            "show_print_pro_button": settings.show_print_pro_button,
            "replace_default_print": settings.replace_default_print,
            "default_paper_size": settings.default_paper_size,
            "default_orientation": settings.default_orientation,
            "show_print_preview": settings.show_print_preview,
            "watermark_on_draft": settings.watermark_on_draft,
            "watermark_text": settings.watermark_text,
        }
    except Exception:
        bootinfo.print_pro = {"enabled": 0}
