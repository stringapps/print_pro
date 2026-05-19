"""
Print Pro - Print Engine
Handles actual dispatching of print jobs to various printer backends.
"""
import frappe
from frappe import _
from frappe.utils.pdf import get_pdf
import socket
import os


def execute_print(doctype, docname, printer_name=None, format_name=None,
                  copies=1, paper_size=None, orientation=None, use_native_format=None):
    """
    Central dispatcher — gets HTML, resolves printer, sends job.
    Returns a result dict.
    """
    # 1. Get rendered HTML
    from print_pro.api import _get_html
    html = _get_html(doctype, docname, format_name, use_native_format)

    # 2. Resolve printer
    if printer_name:
        printer = frappe.get_doc("Print Pro Printer", printer_name)
    else:
        # Use default printer
        default = frappe.get_value("Print Pro Printer", {"is_default": 1, "enabled": 1}, "name")
        if default:
            printer = frappe.get_doc("Print Pro Printer", default)
        else:
            # Fallback: just generate PDF
            return _pdf_output(html, doctype, docname)

    if not printer.enabled:
        frappe.throw(_("Printer '{0}' is disabled.").format(printer.printer_name))

    # 3. Dispatch based on printer type
    ptype = printer.printer_type
    if ptype == "PDF":
        return _pdf_output(html, doctype, docname, printer)
    elif ptype == "Network (IP)":
        return _network_print(html, printer, copies, paper_size, orientation)
    elif ptype == "USB":
        return _usb_print(html, printer, copies)
    elif ptype == "Email":
        return _email_print(html, printer, doctype, docname, copies)
    elif ptype == "Cloud Print":
        return _cloud_print(html, printer, doctype, docname, copies)
    else:
        frappe.throw(_("Unsupported printer type: {0}").format(ptype))


def _pdf_output(html, doctype, docname, printer=None):
    """Generate PDF — either save to path or queue for browser download"""
    options = _build_pdf_options(printer)
    pdf_bytes = get_pdf(html, options)

    save_path = getattr(printer, "pdf_save_path", None) if printer else None
    if save_path:
        filename_fmt = getattr(printer, "pdf_filename_format", "{doctype}-{name}") or "{doctype}-{name}"
        filename = filename_fmt.format(doctype=doctype, name=docname) + ".pdf"
        full_path = os.path.join(save_path, filename)
        os.makedirs(save_path, exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(pdf_bytes)
        return {"type": "file", "path": full_path}
    else:
        # Store in Frappe file manager for browser download
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": f"{doctype}-{docname}.pdf",
            "content": pdf_bytes,
            "is_private": 1,
        })
        file_doc.insert(ignore_permissions=True)
        return {"type": "download", "file_url": file_doc.file_url}


def _network_print(html, printer, copies=1, paper_size=None, orientation=None):
    """Send raw print data over TCP/IP (ESC/POS or RAW)"""
    ip = printer.printer_ip
    port = int(printer.printer_port or 9100)

    pdf_bytes = get_pdf(html, _build_pdf_options(printer))

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((ip, port))
        for _ in range(int(copies or 1)):
            sock.sendall(pdf_bytes)
        sock.close()
        return {"type": "network", "ip": ip, "port": port}
    except Exception as e:
        frappe.throw(_("Network print failed: {0}").format(str(e)))


def _usb_print(html, printer, copies=1):
    """Send to USB printer (requires usb library)"""
    try:
        import usb.core
        import usb.util
        vendor_id = int(printer.usb_vendor_id, 16)
        product_id = int(printer.usb_product_id, 16)
        dev = usb.core.find(idVendor=vendor_id, idProduct=product_id)
        if dev is None:
            frappe.throw(_("USB Printer not found. Check Vendor/Product ID."))
        dev.set_configuration()
        cfg = dev.get_active_configuration()
        intf = cfg[(0, 0)]
        ep = usb.util.find_descriptor(intf, custom_match=lambda e:
            usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
        pdf_bytes = get_pdf(html, _build_pdf_options(printer))
        for _ in range(int(copies or 1)):
            ep.write(pdf_bytes)
        return {"type": "usb"}
    except ImportError:
        frappe.throw(_("PyUSB not installed. Run: pip install pyusb"))
    except Exception as e:
        frappe.throw(_("USB print failed: {0}").format(str(e)))


def _email_print(html, printer, doctype, docname, copies=1):
    """Send document via email as PDF attachment"""
    recipients = [r.strip() for r in (printer.email_recipients or "").split(",") if r.strip()]
    if not recipients:
        frappe.throw(_("No email recipients configured for printer '{0}'.").format(printer.printer_name))

    pdf_bytes = get_pdf(html, _build_pdf_options(printer))

    frappe.sendmail(
        recipients=recipients,
        subject=f"Print: {doctype} - {docname}",
        message=f"<p>Please find attached the printout for {doctype} <b>{docname}</b>.</p>",
        attachments=[{
            "fname": f"{doctype}-{docname}.pdf",
            "fcontent": pdf_bytes,
        }],
    )
    return {"type": "email", "recipients": recipients}


def _cloud_print(html, printer, doctype, docname, copies=1):
    """Placeholder for cloud print integration"""
    frappe.throw(_("Cloud Print is not yet configured. Please contact your administrator."))


def _build_pdf_options(printer=None):
    """Build wkhtmltopdf options from printer settings"""
    opts = {}
    if printer:
        if printer.margin_top:
            opts["margin-top"] = f"{printer.margin_top}mm"
        if printer.margin_right:
            opts["margin-right"] = f"{printer.margin_right}mm"
        if printer.margin_bottom:
            opts["margin-bottom"] = f"{printer.margin_bottom}mm"
        if printer.margin_left:
            opts["margin-left"] = f"{printer.margin_left}mm"
        if printer.orientation:
            opts["orientation"] = printer.orientation
        if printer.paper_size and printer.paper_size not in ("Thermal 80mm", "Thermal 58mm", "Custom"):
            opts["page-size"] = printer.paper_size
    return opts


def test_connection(printer_doc):
    """Test if a printer is reachable"""
    ptype = printer_doc.printer_type
    if ptype == "Network (IP)":
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((printer_doc.printer_ip, int(printer_doc.printer_port or 9100)))
            sock.close()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    elif ptype == "PDF":
        return {"success": True, "message": "PDF printer is always available."}
    else:
        return {"success": True, "message": f"{ptype} printer assumed available."}


def send_test_page(printer_doc):
    """Generate and send a test print page"""
    html = """
    <html><body style="font-family:Arial;padding:40px;text-align:center;">
    <h1 style="color:#1a73e8;">Print Pro Test Page</h1>
    <p>Printer: <strong>{name}</strong></p>
    <p>Type: <strong>{ptype}</strong></p>
    <p>Paper: <strong>{paper}</strong> | Orientation: <strong>{orient}</strong></p>
    <hr/><p style="color:#666;">If you can read this, your printer is working correctly.</p>
    </body></html>
    """.format(
        name=printer_doc.printer_name,
        ptype=printer_doc.printer_type,
        paper=printer_doc.paper_size,
        orient=printer_doc.orientation,
    )
    return execute_print(
        doctype="Print Pro Printer",
        docname=printer_doc.name,
        printer_name=printer_doc.name,
    )
