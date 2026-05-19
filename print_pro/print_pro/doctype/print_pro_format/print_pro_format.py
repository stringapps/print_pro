"""Print Pro Format - Custom print format configuration"""
import frappe
from frappe import _
from frappe.model.document import Document


class PrintProFormat(Document):

    def validate(self):
        self._validate_template()
        self._set_single_default()

    def _validate_template(self):
        if self.use_erpnext_format and not self.erpnext_print_format:
            frappe.throw(_(
                "Please select an ERPNext Print Format when "
                "'Use ERPNext Print Format as Base' is checked."
            ))
        if self.use_custom_template and not self.custom_html:
            frappe.throw(_(
                "Please enter Custom HTML when "
                "'Use Custom HTML Template' is checked."
            ))

    def _set_single_default(self):
        """Only one format per doctype can be default."""
        if self.is_default:
            frappe.db.set_value(
                "Print Pro Format",
                {
                    "is_default": 1,
                    "document_type": self.document_type,
                    "name": ["!=", self.name],
                },
                "is_default",
                0,
            )

    # ------------------------------------------------------------------ #
    def get_rendered_html(self, doc_name):
        """
        Render the print format HTML for *doc_name*.

        Pagination is pre-calculated here in Python and exposed as the
        ``pages`` variable so that Jinja templates only need a plain
        ``{% for page_items in pages %}`` loop with zero arithmetic.
        This is required because Frappe runs Jinja inside a
        SandboxedEnvironment that blocks many arithmetic/filter operations.
        """
        doc = frappe.get_doc(self.document_type, doc_name)

        # Pre-fetch Company so templates never call frappe.get_doc()
        # inside Jinja (unsafe / blocked in the sandbox).
        co = frappe._dict()
        if self.with_header and doc.get("company"):
            try:
                co = frappe.get_doc("Company", doc.company)
            except Exception:
                co = frappe._dict()

        # ── Pagination ────────────────────────────────────────────────
        # Tax Invoice has an extra column (barcode/tax), so fits fewer rows.
        ipp = 15 if "Tax Invoice" in (self.format_name or "") else 16
        raw_items = list(doc.items) if getattr(doc, "items", None) else []
        if raw_items:
            pages = [raw_items[i: i + ipp] for i in range(0, len(raw_items), ipp)]
        else:
            pages = [[]]          # always at least one page
        n_pages = len(pages)

        context = {
            "doc":                    doc,
            "frappe":                 frappe,
            "co":                     co,
            "pages":                  pages,
            "n_pages":                n_pages,
            "with_header":            int(self.with_header or 1),
            "repeat_header_on_pages": int(self.repeat_header_on_pages or 0),
            "dot_matrix_mode":        int(self.dot_matrix_mode or 0),
        }

        # ── Render ────────────────────────────────────────────────────
        if self.use_custom_template and self.custom_html:
            html = frappe.render_template(self.custom_html, context)

        elif self.use_erpnext_format and self.erpnext_print_format:
            html = frappe.get_print(
                self.document_type, doc_name,
                print_format=self.erpnext_print_format,
            )
        else:
            html = frappe.get_print(self.document_type, doc_name)

        # ── Dot-matrix / plain mode ───────────────────────────────────
        if self.dot_matrix_mode:
            dm_css = (
                "<style>\n"
                "* { background:#fff !important; background-color:#fff !important;\n"
                "    background-image:none !important; color:#000 !important;\n"
                "    box-shadow:none !important; text-shadow:none !important; }\n"
                "body { font-family:\'Courier New\',Courier,monospace !important;"
                " font-size:11px !important; }\n"
                "</style>\n"
            )
            html = (
                html.replace("</head>", dm_css + "</head>", 1)
                if "</head>" in html
                else dm_css + html
            )

        return html


# ─────────────────────────────────────────────────────────────────────────
def has_permission(doc, user=None, ptype="read"):
    return frappe.has_permission("Print Pro Format", ptype, doc, user=user)


@frappe.whitelist()
def get_formats_for_doctype(doctype):
    return frappe.get_all(
        "Print Pro Format",
        filters={"document_type": doctype, "enabled": 1},
        fields=["name", "format_name", "is_default",
                "paper_size", "assigned_printer"],
        order_by="is_default desc, format_name asc",
    )


@frappe.whitelist()
def get_default_format(doctype):
    fmt = frappe.get_value(
        "Print Pro Format",
        {"document_type": doctype, "is_default": 1, "enabled": 1},
        "name",
    )
    if fmt:
        return frappe.get_doc("Print Pro Format", fmt)
    all_fmt = get_formats_for_doctype(doctype)
    if all_fmt:
        return frappe.get_doc("Print Pro Format", all_fmt[0]["name"])
    return None
