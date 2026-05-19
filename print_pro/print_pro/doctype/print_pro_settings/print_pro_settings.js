// Print Pro Settings - Client Script
frappe.ui.form.on('Print Pro Settings', {
    refresh(frm) {
        frm.add_custom_button(__('Test Default Printer'), () => {
            frappe.call({
                method: 'print_pro.api.test_printer',
                args: { printer: frm.doc.default_printer },
                callback(r) {
                    if (r.message && r.message.success) {
                        frappe.show_alert({ message: __('Printer test successful!'), indicator: 'green' });
                    } else {
                        frappe.show_alert({ message: __('Printer test failed. Check configuration.'), indicator: 'red' });
                    }
                }
            });
        }, __('Actions'));
    },
    replace_default_print(frm) {
        if (frm.doc.replace_default_print) {
            frappe.show_alert({
                message: __('Print Pro will now replace the default ERPNext print button across all supported documents.'),
                indicator: 'blue'
            });
        }
    }
});
