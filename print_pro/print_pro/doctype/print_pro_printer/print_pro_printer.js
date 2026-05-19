// Print Pro Printer - Client Script
frappe.ui.form.on('Print Pro Printer', {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Test Connection'), () => {
                frappe.call({
                    method: 'print_pro.api.test_printer',
                    args: { printer: frm.doc.name },
                    freeze: true,
                    freeze_message: __('Testing printer connection...'),
                    callback(r) {
                        const res = r.message;
                        if (res && res.success) {
                            frappe.show_alert({ message: __('Connection successful! ✓'), indicator: 'green' });
                        } else {
                            frappe.show_alert({ message: __('Connection failed: ') + (res && res.error || 'Unknown error'), indicator: 'red' });
                        }
                    }
                });
            }, __('Actions'));

            frm.add_custom_button(__('Print Test Page'), () => {
                frappe.call({
                    method: 'print_pro.api.print_test_page',
                    args: { printer: frm.doc.name },
                    freeze: true,
                    freeze_message: __('Sending test page...'),
                    callback(r) {
                        if (r.message && r.message.success) {
                            frappe.show_alert({ message: __('Test page sent!'), indicator: 'green' });
                        }
                    }
                });
            }, __('Actions'));
        }
    },

    printer_type(frm) {
        // Show/hide sections based on printer type
        const networkFields = ['printer_ip', 'printer_port'];
        const usbFields = ['usb_vendor_id', 'usb_product_id'];
        const pdfFields = ['pdf_save_path', 'pdf_filename_format'];

        networkFields.forEach(f => frm.set_df_property(f, 'hidden', frm.doc.printer_type !== 'Network (IP)'));
        usbFields.forEach(f => frm.set_df_property(f, 'hidden', frm.doc.printer_type !== 'USB'));
        pdfFields.forEach(f => frm.set_df_property(f, 'hidden', frm.doc.printer_type !== 'PDF'));
    },

    is_default(frm) {
        if (frm.doc.is_default) {
            frappe.show_alert({
                message: __('This printer will be used as default across all documents.'),
                indicator: 'blue'
            });
        }
    }
});
