"""
Print Pro - Main API
All whitelisted endpoints for the Print Pro frontend
"""
import frappe
from frappe import _
from frappe.utils.pdf import get_pdf
import json


# ─── Core Print API ──────────────────────────────────────────────────────────

@frappe.whitelist()
def get_print_dialog_data(doctype, docname):
    """
    Returns all data needed to populate the Print Pro dialog:
    - Available print formats for this doctype
    - Available printers
    - Default selections
    - Document info
    """
    frappe.has_permission(doctype, "print", throw=True)

    from print_pro.print_pro.doctype.print_pro_format.print_pro_format import get_formats_for_doctype
    from print_pro.print_pro.doctype.print_pro_printer.print_pro_printer import get_printers_for_doctype
    from print_pro.print_pro.doctype.print_pro_settings.print_pro_settings import PrintProSettings

    settings = PrintProSettings.get_settings()

    # Get ERPNext native print formats too
    native_formats = frappe.get_all(
        "Print Format",
        filters={"doc_type": doctype, "disabled": 0},
        fields=["name", "default_print_language"],
        order_by="name asc",
    )

    pro_formats = get_formats_for_doctype(doctype)
    printers = get_printers_for_doctype(doctype)

    # Get document info
    doc = frappe.get_doc(doctype, docname)

    return {
        "pro_formats": pro_formats,
        "native_formats": native_formats,
        "printers": printers,
        "settings": {
            "default_paper_size": settings.default_paper_size,
            "default_orientation": settings.default_orientation,
            "show_preview": settings.show_print_preview,
            "allow_custom_css": settings.allow_custom_css,
            "watermark_on_draft": settings.watermark_on_draft,
            "watermark_text": settings.watermark_text,
        },
        "doc_info": {
            "name": doc.name,
            "doctype": doctype,
            "status": getattr(doc, "status", None) or getattr(doc, "docstatus", None),
            "company": getattr(doc, "company", None),
        }
    }


@frappe.whitelist()
def print_document(doctype, docname, printer=None, print_format=None,
                   copies=1, paper_size=None, orientation=None,
                   use_native_format=None):
    """
    Main print action — dispatches to correct printer backend.
    For PDF printer, returns a file_url the browser can open.
    """
    frappe.has_permission(doctype, "print", throw=True)

    from print_pro.print_pro.doctype.print_pro_log.print_pro_log import create_log
    from print_pro.utils.print_engine import execute_print

    copies = int(copies or 1)

    try:
        result = execute_print(
            doctype=doctype,
            docname=docname,
            printer_name=printer,
            format_name=print_format,
            copies=copies,
            paper_size=paper_size,
            orientation=orientation,
            use_native_format=use_native_format,
        )
        create_log(
            document_type=doctype,
            document_name=docname,
            status="Success",
            printer=printer,
            print_format=print_format,
            copies=copies,
            paper_size=paper_size,
            orientation=orientation,
        )
        return {"success": True, "message": _("Print job sent successfully."), "result": result}

    except Exception as e:
        create_log(
            document_type=doctype,
            document_name=docname,
            status="Failed",
            printer=printer,
            print_format=print_format,
            copies=copies,
            error=str(e),
        )
        frappe.log_error(frappe.get_traceback(), "Print Pro - Print Failed")
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_pdf_for_download(doctype, docname, print_format=None, use_native_format=None,
                         paper_size=None, orientation=None):
    """Generate PDF and trigger browser download (Content-Disposition: attachment)"""
    frappe.has_permission(doctype, "print", throw=True)

    html = _get_html(doctype, docname, print_format, use_native_format)

    # Build options
    opts = {}
    if orientation:
        opts["orientation"] = orientation
    if paper_size and paper_size not in ("Thermal 80mm", "Thermal 58mm", "Custom"):
        opts["page-size"] = paper_size

    pdf_bytes = get_pdf(html, opts)

    # Set Frappe download response — triggers browser "Save As" dialog
    frappe.local.response.filename = "{}-{}.pdf".format(
        doctype.replace(" ", "-"), docname.replace(" ", "-").replace("/", "-")
    )
    frappe.local.response.filecontent = pdf_bytes
    frappe.local.response.type = "download"


@frappe.whitelist()
def preview_format(doctype, name, format=None, use_native=None,
                   paper_size=None, orientation=None):
    """
    Return rendered HTML for the print preview iframe.
    Returns JSON: {"html": "<full document HTML>"}
    """
    frappe.has_permission(doctype, "print", throw=True)

    try:
        html = _get_html(doctype, name, format, use_native)

        # Inject responsive wrapper so preview fits inside the dialog iframe
        preview_css = """
        <style>
        html, body { margin: 0; padding: 0; background: #fff; }
        body { transform-origin: top left; }
        .pp { padding: 20px !important; }
        </style>
        """
        if "</head>" in html:
            html = html.replace("</head>", preview_css + "</head>", 1)
        else:
            html = preview_css + html

        return {"html": html, "success": True}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Print Pro - Preview Failed")
        return {"html": None, "success": False, "error": str(e)}


@frappe.whitelist()
def detect_usb_printers():
    """
    Detect USB printers connected to the server.
    Returns list of {vendor_id, product_id, description}.
    Requires pyusb: pip install pyusb
    """
    try:
        import usb.core
        import usb.util

        all_devices = usb.core.find(find_all=True)
        printers = []

        for dev in all_devices:
            is_printer = False
            try:
                # USB printer class = 7
                if dev.bDeviceClass == 7:
                    is_printer = True
                else:
                    for cfg in dev:
                        for intf in cfg:
                            if intf.bInterfaceClass == 7:
                                is_printer = True
                                break
                        if is_printer:
                            break
            except Exception:
                pass

            if is_printer:
                try:
                    vid = "0x{:04x}".format(dev.idVendor)
                    pid = "0x{:04x}".format(dev.idProduct)
                    try:
                        desc = usb.util.get_string(dev, dev.iProduct) or "USB Printer"
                    except Exception:
                        desc = "USB Printer ({} {})".format(vid, pid)
                    printers.append({
                        "vendor_id": vid,
                        "product_id": pid,
                        "description": desc,
                    })
                except Exception:
                    pass

        if not printers:
            # Also return all HID/unknown devices so user can identify manually
            return {"printers": [], "message": "No USB printer class devices found. Is the printer connected and powered on?"}

        return {"printers": printers, "message": "{} printer(s) detected.".format(len(printers))}

    except ImportError:
        return {
            "printers": [],
            "error": "PyUSB not installed",
            "message": "Run on your server: pip install pyusb --break-system-packages"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Print Pro - USB Detect Failed")
        return {"printers": [], "error": str(e)}


@frappe.whitelist()
def test_printer(printer):
    """Test printer connectivity"""
    if not printer:
        return {"success": False, "error": "No printer specified"}

    try:
        doc = frappe.get_doc("Print Pro Printer", printer)
        from print_pro.utils.print_engine import test_connection
        return test_connection(doc)
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def print_test_page(printer):
    """Send a test page to printer"""
    try:
        doc = frappe.get_doc("Print Pro Printer", printer)
        from print_pro.utils.print_engine import send_test_page
        return send_test_page(doc)
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_print_log(doctype, docname):
    """Get print history for a document"""
    return frappe.get_all(
        "Print Pro Log",
        filters={"document_type": doctype, "document_name": docname},
        fields=["name", "status", "printer", "print_format", "printed_by", "printed_on", "copies"],
        order_by="printed_on desc",
        limit=20,
    )


@frappe.whitelist()
def get_settings():
    """Return Print Pro Settings for frontend"""
    from print_pro.print_pro.doctype.print_pro_settings.print_pro_settings import PrintProSettings
    s = PrintProSettings.get_settings()
    return {
        "enabled": s.enabled,
        "show_print_pro_button": s.show_print_pro_button,
        "replace_default_print": s.replace_default_print,
        "default_paper_size": s.default_paper_size,
        "default_orientation": s.default_orientation,
        "show_print_preview": s.show_print_preview,
        "watermark_on_draft": s.watermark_on_draft,
        "watermark_text": s.watermark_text,
    }


# ─── Internal helpers ────────────────────────────────────────────────────────

def _get_html(doctype, docname, format_name=None, use_native_format=None):
    """Resolve and render HTML for a document"""
    if format_name and not use_native_format:
        # Use Print Pro Format
        fmt = frappe.get_doc("Print Pro Format", format_name)
        return fmt.get_rendered_html(docname)
    elif use_native_format:
        # Use ERPNext native format
        return frappe.get_print(doctype, docname, print_format=use_native_format)
    else:
        # Auto-detect best format
        from print_pro.print_pro.doctype.print_pro_format.print_pro_format import get_default_format
        fmt = get_default_format(doctype)
        if fmt:
            return fmt.get_rendered_html(docname)
        return frappe.get_print(doctype, docname)
