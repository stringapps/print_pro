"""
Run on server:
  cd /home/erpuser/frappe-bench1
  bench --site testrtf.stringitsolution.org execute print_pro.fix_templates_db.run
"""
import frappe

def get_sales_invoice_html():
    return """<style>
* { box-sizing:border-box; margin:0; padding:0; }
body { font-family:'Segoe UI',Arial,sans-serif; font-size:10pt; color:#111; background:#fff; }
.pp-page { width:100%; padding:10mm 12mm; }
.pp-page-break { page-break-after:always; }
.company-header { text-align:center; margin-bottom:4px; }
.company-name { font-size:15pt; font-weight:700; letter-spacing:1px; text-transform:uppercase; }
.company-sub { font-size:9pt; margin-top:2px; }
.company-contact { font-size:8.5pt; margin-top:2px; color:#444; }
hr.divider-thick { border:none; border-top:2px solid #111; margin:5px 0; }
hr.divider-thin  { border:none; border-top:1px solid #888; margin:4px 0; }
.doc-title-wrap { text-align:center; margin:4px 0; }
.doc-title { font-size:12pt; font-weight:700; letter-spacing:2px; }
.meta-outer { width:100%; border-collapse:collapse; margin:6px 0; }
.meta-outer td { vertical-align:top; font-size:9pt; }
.meta-cell { width:50%; }
.meta-label { color:#444; width:100px; }
.meta-value { font-weight:600; }
.items-table { width:100%; border-collapse:collapse; margin:6px 0; font-size:8.5pt; }
.items-table thead tr { background:#1e3a8a; color:#fff; }
.items-table th { padding:4px 5px; text-align:center; border:1px solid #bbb; font-size:8pt; }
.items-table td { padding:3px 5px; border:1px solid #ccc; text-align:center; }
.items-table td.left { text-align:left; }
.items-table td.bold { font-weight:600; }
.item-row:nth-child(even) { background:#f5f8ff; }
.empty-row td { height:16px; }
.totals-outer { width:100%; border-collapse:collapse; margin:6px 0; font-size:9pt; }
.totals-label { text-align:right; padding:2px 8px; color:#444; }
.totals-value { text-align:right; padding:2px 6px; font-weight:600; width:100px; }
.grand-row td { font-size:10pt; font-weight:700; border-top:2px solid #111; border-bottom:2px solid #111; }
.words-row { font-size:8pt; font-style:italic; color:#555; margin:4px 0; padding:3px 6px; border-top:1px solid #ccc; }
.sig-table { width:100%; border-collapse:collapse; margin-top:8px; }
.sig-table td { text-align:center; border-top:1px solid #888; padding-top:4px; font-size:8.5pt; width:33%; }
.print-footer { text-align:center; font-size:7.5pt; color:#888; margin-top:6px; border-top:1px dashed #ccc; padding-top:3px; }
</style>
{% for page_items in pages %}
{% set is_last = loop.last %}
{% set pg = loop.index %}
<div class="pp-page{% if not is_last %} pp-page-break{% endif %}">
{% if with_header %}
<div class="company-header">
<div class="company-name">{{ doc.company | upper }}</div>
{% if co and co.tax_id %}<div class="company-sub">TRN : {{ co.tax_id }}</div>{% endif %}
{% if co and (co.phone_no or co.email_id) %}
<div class="company-contact">{% if co.phone_no %}Tel : {{ co.phone_no }}{% endif %}{% if co.phone_no and co.email_id %} &nbsp;&nbsp; {% endif %}{% if co.email_id %}Email : {{ co.email_id }}{% endif %}</div>
{% endif %}
</div>
<hr class="divider-thick">
{% endif %}
<div class="doc-title-wrap"><span class="doc-title">SALES INVOICE</span></div>
<hr class="divider-thin">
<table class="meta-outer"><tr>
<td class="meta-cell"><table style="width:100%;border-collapse:collapse;">
<tr><td class="meta-label">Client</td><td>:</td><td class="meta-value">{{ doc.customer_name | upper }}</td></tr>
{% if doc.tax_id %}<tr><td class="meta-label">TRN</td><td>:</td><td class="meta-value">{{ doc.tax_id }}</td></tr>{% endif %}
{% if doc.address_display %}<tr><td class="meta-label">Address</td><td>:</td><td>{{ doc.address_display | striptags | truncate(80) }}</td></tr>{% endif %}
{% if doc.contact_display %}<tr><td class="meta-label">Contact</td><td>:</td><td>{{ doc.contact_display | striptags }}</td></tr>{% endif %}
</table></td>
<td class="meta-cell" style="padding-left:10px;"><table style="width:100%;border-collapse:collapse;">
<tr><td class="meta-label">Invoice No</td><td>:</td><td class="meta-value">{{ doc.name }}</td></tr>
<tr><td class="meta-label">Date</td><td>:</td><td>{{ doc.posting_date }}</td></tr>
{% if doc.due_date %}<tr><td class="meta-label">Due Date</td><td>:</td><td>{{ doc.due_date }}</td></tr>{% endif %}
{% if doc.payment_terms_template %}<tr><td class="meta-label">Terms</td><td>:</td><td>{{ doc.payment_terms_template }}</td></tr>{% endif %}
{% if doc.po_no %}<tr><td class="meta-label">PO No</td><td>:</td><td>{{ doc.po_no }}</td></tr>{% endif %}
<tr><td class="meta-label">Page</td><td>:</td><td>{{ pg }} / {{ n_pages }}</td></tr>
</table></td>
</tr></table>
<hr class="divider-thick">
<table class="items-table">
<thead><tr>
<th style="width:4%;">S.No</th><th style="width:12%;">Item Code</th><th style="width:30%;text-align:left;">Description</th>
<th style="width:6%;">Qty</th><th style="width:6%;">UOM</th><th style="width:12%;">Unit Price</th><th style="width:8%;">Disc%</th><th style="width:12%;">Amount</th>
</tr></thead>
<tbody>
{% for item in page_items %}
<tr class="item-row">
<td>{{ item.idx }}</td>
<td style="font-size:7.5pt;">{{ item.item_code }}</td>
<td class="left bold">{{ item.item_name | upper }}</td>
<td>{{ item.qty | int }}</td>
<td>{{ item.uom or 'Pcs' }}</td>
<td>{{ "%.2f" % ((item.price_list_rate or item.rate or 0) | float) }}</td>
<td>{{ "%.2f" % ((item.discount_percentage or 0) | float) }}</td>
<td>{{ "%.2f" % ((item.net_amount or item.amount or 0) | float) }}</td>
</tr>
{% endfor %}
{% if is_last %}{% set n_filled = page_items | length %}{% if n_filled < 8 %}{% for i in range(8 - n_filled) %}<tr class="empty-row"><td colspan="8">&nbsp;</td></tr>{% endfor %}{% endif %}{% endif %}
</tbody>
</table>
{% if is_last %}
<div class="words-row">Amount in Words: {{ doc.in_words | upper if doc.in_words else '' }}</div>
<table class="totals-outer">
<tr><td class="totals-label">Sub Total :</td><td class="totals-value">{{ "%.2f" % ((doc.total or 0) | float) }}</td></tr>
{% set tax_amt = (doc.total_taxes_and_charges or 0) | float %}
{% if tax_amt > 0 %}<tr><td class="totals-label">VAT (5%) :</td><td class="totals-value">{{ "%.2f" % tax_amt }}</td></tr>{% endif %}
{% set disc = (doc.discount_amount or 0) | float %}
{% if disc > 0 %}<tr><td class="totals-label">Discount :</td><td class="totals-value">- {{ "%.2f" % disc }}</td></tr>{% endif %}
<tr class="grand-row"><td class="totals-label">GRAND TOTAL :</td><td class="totals-value">{{ "%.2f" % ((doc.grand_total or 0) | float) }}</td></tr>
</table>
<hr class="divider-thick">
<table class="sig-table"><tr><td>Prepared By</td><td>Authorised Signatory</td><td>Received By</td></tr></table>
<div class="print-footer">Printed By: {{ doc.owner }} &nbsp;|&nbsp; {{ doc.company }}</div>
{% endif %}
</div>
{% endfor %}"""

def get_tax_invoice_html():
    return """<style>
* { box-sizing:border-box; margin:0; padding:0; }
body { font-family:'Segoe UI',Arial,sans-serif; font-size:10pt; color:#111; background:#fff; }
.pp-page { width:100%; padding:10mm 12mm; }
.pp-page-break { page-break-after:always; }
.company-header { text-align:center; margin-bottom:4px; }
.company-name { font-size:15pt; font-weight:700; letter-spacing:1px; text-transform:uppercase; }
.company-sub { font-size:9pt; margin-top:2px; }
.company-contact { font-size:8.5pt; margin-top:2px; color:#444; }
hr.divider-thick { border:none; border-top:2px solid #111; margin:5px 0; }
hr.divider-thin  { border:none; border-top:1px solid #888; margin:4px 0; }
.doc-title-wrap { text-align:center; margin:4px 0; }
.doc-title { font-size:12pt; font-weight:700; letter-spacing:2px; }
.meta-outer { width:100%; border-collapse:collapse; margin:6px 0; }
.meta-outer td { vertical-align:top; font-size:9pt; }
.meta-cell { width:50%; }
.meta-label { color:#444; width:100px; }
.meta-value { font-weight:600; }
.items-table { width:100%; border-collapse:collapse; margin:6px 0; font-size:8.5pt; }
.items-table thead tr { background:#1e3a8a; color:#fff; }
.items-table th { padding:4px 5px; text-align:center; border:1px solid #bbb; font-size:8pt; }
.items-table td { padding:3px 5px; border:1px solid #ccc; text-align:center; }
.items-table td.left { text-align:left; }
.items-table td.bold { font-weight:600; }
.item-row:nth-child(even) { background:#f5f8ff; }
.empty-row td { height:16px; }
.totals-outer { width:100%; border-collapse:collapse; margin:6px 0; font-size:9pt; }
.totals-label { text-align:right; padding:2px 8px; color:#444; }
.totals-value { text-align:right; padding:2px 6px; font-weight:600; width:100px; }
.grand-row td { font-size:10pt; font-weight:700; border-top:2px solid #111; border-bottom:2px solid #111; }
.words-row { font-size:8pt; font-style:italic; color:#555; margin:4px 0; padding:3px 6px; border-top:1px solid #ccc; }
.sig-table { width:100%; border-collapse:collapse; margin-top:8px; }
.sig-table td { text-align:center; border-top:1px solid #888; padding-top:4px; font-size:8.5pt; width:25%; }
.print-footer { text-align:center; font-size:7.5pt; color:#888; margin-top:6px; border-top:1px dashed #ccc; padding-top:3px; }
</style>
{% for page_items in pages %}
{% set is_last = loop.last %}
{% set pg = loop.index %}
<div class="pp-page{% if not is_last %} pp-page-break{% endif %}">
{% if with_header %}
<div class="company-header">
<div class="company-name">{{ doc.company | upper }}</div>
{% if co and co.tax_id %}<div class="company-sub">TRN : {{ co.tax_id }}</div>{% endif %}
{% if co and (co.phone_no or co.email_id) %}
<div class="company-contact">{% if co.phone_no %}Tel : {{ co.phone_no }}{% endif %}{% if co.phone_no and co.email_id %} &nbsp;&nbsp; {% endif %}{% if co.email_id %}Email : {{ co.email_id }}{% endif %}</div>
{% endif %}
</div>
<hr class="divider-thick">
{% endif %}
<div class="doc-title-wrap"><span class="doc-title">TAX INVOICE</span></div>
<hr class="divider-thin">
<table class="meta-outer"><tr>
<td class="meta-cell"><table style="width:100%;border-collapse:collapse;">
<tr><td class="meta-label">Client</td><td>:</td><td class="meta-value">{{ doc.customer_name | upper }}</td></tr>
{% if doc.tax_id %}<tr><td class="meta-label">TRN</td><td>:</td><td class="meta-value">{{ doc.tax_id }}</td></tr>{% endif %}
{% if doc.address_display %}<tr><td class="meta-label">Address</td><td>:</td><td>{{ doc.address_display | striptags | truncate(80) }}</td></tr>{% endif %}
{% if doc.contact_display %}<tr><td class="meta-label">Contact</td><td>:</td><td>{{ doc.contact_display | striptags }}</td></tr>{% endif %}
</table></td>
<td class="meta-cell" style="padding-left:10px;"><table style="width:100%;border-collapse:collapse;">
<tr><td class="meta-label">Invoice No</td><td>:</td><td class="meta-value">{{ doc.name }}</td></tr>
<tr><td class="meta-label">Date</td><td>:</td><td>{{ doc.posting_date }}</td></tr>
{% if doc.due_date %}<tr><td class="meta-label">Due Date</td><td>:</td><td>{{ doc.due_date }}</td></tr>{% endif %}
{% if doc.po_no %}<tr><td class="meta-label">PO No</td><td>:</td><td>{{ doc.po_no }}</td></tr>{% endif %}
<tr><td class="meta-label">Page</td><td>:</td><td>{{ pg }} / {{ n_pages }}</td></tr>
</table></td>
</tr></table>
<hr class="divider-thick">
<table class="items-table">
<thead><tr>
<th style="width:4%;">S.No</th><th style="width:10%;">Barcode</th><th style="width:25%;text-align:left;">Description</th>
<th style="width:5%;">Qty</th><th style="width:5%;">UOM</th><th style="width:11%;">U.Price</th>
<th style="width:7%;">Disc%</th><th style="width:8%;">Tax%</th><th style="width:11%;">Amount</th>
</tr></thead>
<tbody>
{% for item in page_items %}
<tr class="item-row">
<td>{{ item.idx }}</td>
<td style="font-size:7pt;">{{ item.barcode or item.item_code }}</td>
<td class="left bold">{{ item.item_name | upper }}</td>
<td>{{ item.qty | int }}</td>
<td>{{ item.uom or 'Pcs' }}</td>
<td>{{ "%.2f" % ((item.price_list_rate or item.rate or 0) | float) }}</td>
<td>{{ "%.2f" % ((item.discount_percentage or 0) | float) }}</td>
<td>{{ "%.1f" % ((item.tax_rate or 0) | float) }}%</td>
<td>{{ "%.2f" % ((item.net_amount or item.amount or 0) | float) }}</td>
</tr>
{% endfor %}
{% if is_last %}{% set n_filled = page_items | length %}{% if n_filled < 8 %}{% for i in range(8 - n_filled) %}<tr class="empty-row"><td colspan="9">&nbsp;</td></tr>{% endfor %}{% endif %}{% endif %}
</tbody>
</table>
{% if is_last %}
<div class="words-row">Amount in Words: {{ doc.in_words | upper if doc.in_words else '' }}</div>
<table class="totals-outer">
<tr><td class="totals-label">TOTAL :</td><td class="totals-value">{{ "%.2f" % ((doc.total or 0) | float) }}</td></tr>
{% set tax_amt = (doc.total_taxes_and_charges or 0) | float %}
<tr><td class="totals-label">Tax Amount :</td><td class="totals-value">{{ "%.2f" % tax_amt }}</td></tr>
<tr class="grand-row"><td class="totals-label">NET AMOUNT :</td><td class="totals-value">{{ "%.2f" % ((doc.grand_total or 0) | float) }}</td></tr>
</table>
<hr class="divider-thick">
<table class="sig-table"><tr><td>Received By</td><td>Supervisor</td><td>Driver Signature</td><td>Vehicle No</td></tr></table>
<div class="print-footer">Printed By: {{ doc.owner }} &nbsp;|&nbsp; {{ doc.company }}</div>
{% endif %}
</div>
{% endfor %}"""


def run():
    updates = {
        "Print Pro - Sales Invoice": {
            "custom_html": get_sales_invoice_html(),
            "document_type": "Sales Invoice",
        },
        "Print Pro - Tax Invoice": {
            "custom_html": get_tax_invoice_html(),
            "document_type": "Sales Invoice",
        },
    }

    for fmt_name, vals in updates.items():
        exists = frappe.db.exists("Print Pro Format", fmt_name)
        if exists:
            frappe.db.set_value("Print Pro Format", fmt_name, {
                "custom_html": vals["custom_html"],
                "use_custom_template": 1,
                "use_erpnext_format": 0,
                "repeat_header_on_pages": 0,
            })
            frappe.db.commit()
            print(f"  UPDATED: {fmt_name}")
        else:
            print(f"  NOT FOUND: {fmt_name} — run bench migrate first")

    frappe.clear_cache()
    print("Done. Templates force-updated directly in database.")
