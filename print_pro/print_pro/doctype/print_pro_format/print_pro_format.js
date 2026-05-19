// Print Pro Format - Client Script
frappe.ui.form.on('Print Pro Format', {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Preview'), () => {
                frappe.prompt(
                    [{ label: __('Document Name'), fieldname: 'doc_name', fieldtype: 'Data', reqd: 1 }],
                    (values) => {
                        window.open(
                            `/api/method/print_pro.api.preview_format?format=${frm.doc.name}&doctype=${frm.doc.document_type}&name=${values.doc_name}`,
                            '_blank'
                        );
                    },
                    __('Preview Format'),
                    __('Preview')
                );
            }, __('Actions'));

            frm.add_custom_button(__('Duplicate Format'), () => {
                frappe.call({
                    method: 'frappe.client.copy_doc',
                    args: { doc: frm.doc },
                    callback(r) {
                        if (r.message) {
                            frappe.set_route('Form', 'Print Pro Format', r.message.name);
                        }
                    }
                });
            }, __('Actions'));
        }
    },

    use_erpnext_format(frm) {
        if (frm.doc.use_erpnext_format) {
            frm.set_value('use_custom_template', 0);
        }
    },

    use_custom_template(frm) {
        if (frm.doc.use_custom_template) {
            frm.set_value('use_erpnext_format', 0);
            if (!frm.doc.custom_html) {
                frm.set_value('custom_html',
                    `<!-- Print Pro Custom Template -->
<!-- Available variables: doc, frappe -->
<div class="print-pro-doc">
    <h2>{{ doc.name }}</h2>
    <p>{{ doc.doctype }} - {{ doc.company }}</p>
    <!-- Add your custom HTML here -->
</div>`
                );
            }
        }
    },

    document_type(frm) {
        if (frm.doc.document_type) {
            // Load available ERPNext print formats for this doctype
            frm.set_query('erpnext_print_format', () => {
                return { filters: { doc_type: frm.doc.document_type } };
            });
        }
    }
});
