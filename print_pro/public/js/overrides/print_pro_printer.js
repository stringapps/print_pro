// Print Pro — Printer DocType form JS
// Adds: Detect USB Printers, Test Connection, Print Test Page buttons

frappe.ui.form.on('Print Pro Printer', {

    refresh: function(frm) {
        frm.trigger('_update_buttons');
    },

    printer_type: function(frm) {
        frm.trigger('_update_buttons');
    },

    _update_buttons: function(frm) {
        // Remove old custom buttons before re-adding
        frm.clear_custom_buttons();

        var ptype = frm.doc.printer_type;

        // ── Test Connection ───────────────────────────────────────────────────
        if (!frm.is_new()) {
            frm.add_custom_button(__('🔌 Test Connection'), function() {
                frappe.call({
                    method: 'print_pro.api.test_printer',
                    args: { printer: frm.doc.name },
                    freeze: true,
                    freeze_message: __('Testing connection...'),
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            frappe.show_alert({
                                message: __('✓ Printer is reachable!') + (r.message.message ? '  ' + r.message.message : ''),
                                indicator: 'green'
                            }, 6);
                        } else {
                            frappe.show_alert({
                                message: __('✗ Connection failed: ') + (r.message && r.message.error || 'Unknown error'),
                                indicator: 'red'
                            }, 8);
                        }
                    }
                });
            }, __('Actions'));

            frm.add_custom_button(__('🖨 Print Test Page'), function() {
                frappe.confirm(
                    __('Send a test page to <b>{0}</b>?').replace('{0}', frm.doc.printer_name),
                    function() {
                        frappe.call({
                            method: 'print_pro.api.print_test_page',
                            args: { printer: frm.doc.name },
                            freeze: true, freeze_message: __('Sending test page...'),
                            callback: function(r) {
                                if (r.message && r.message.success !== false) {
                                    frappe.show_alert({ message: __('✓ Test page sent!'), indicator: 'green' }, 5);
                                } else {
                                    frappe.show_alert({
                                        message: __('✗ Test failed: ') + (r.message && r.message.error || ''),
                                        indicator: 'red'
                                    }, 8);
                                }
                            }
                        });
                    }
                );
            }, __('Actions'));
        }

        // ── USB: Detect button ────────────────────────────────────────────────
        if (ptype === 'USB') {
            frm.add_custom_button(__('🔍 Detect USB Printers'), function() {
                frappe.call({
                    method: 'print_pro.api.detect_usb_printers',
                    freeze: true,
                    freeze_message: __('Scanning USB ports...'),
                    callback: function(r) {
                        var msg = r.message || {};

                        // PyUSB not installed
                        if (msg.error === 'PyUSB not installed') {
                            frappe.msgprint({
                                title: __('PyUSB Required'),
                                message: __(
                                    '<p>PyUSB is not installed on the server.</p>'
                                    + '<p>Run this command on your ERPNext server:</p>'
                                    + '<pre style="background:#f1f5f9;padding:8px;border-radius:4px;">'
                                    + 'pip install pyusb --break-system-packages</pre>'
                                    + '<p>Then restart the bench and try again.</p>'
                                ),
                                indicator: 'orange'
                            });
                            return;
                        }

                        var printers = msg.printers || [];
                        if (!printers.length) {
                            frappe.msgprint({
                                title: __('No USB Printers Found'),
                                message: __(
                                    '<p>' + (msg.message || 'No USB printer class devices detected.') + '</p>'
                                    + '<ul style="margin-top:8px;font-size:12px;">'
                                    + '<li>Make sure the printer is connected and powered on</li>'
                                    + '<li>Try a different USB cable or port</li>'
                                    + '<li>Check that your OS can see the device (<code>lsusb</code>)</li>'
                                    + '</ul>'
                                    + '<p style="margin-top:8px;font-size:12px;color:#64748b;">'
                                    + 'If you know the Vendor ID and Product ID, you can enter them manually below.</p>'
                                ),
                                indicator: 'orange'
                            });
                            return;
                        }

                        // ── Show selection dialog ─────────────────────────────
                        var opts = printers.map(function(p) {
                            return p.vendor_id + '  :  ' + p.product_id + '   —   ' + p.description;
                        });

                        var sel_dialog = new frappe.ui.Dialog({
                            title: __('Detected USB Printers'),
                            fields: [
                                {
                                    label: __('Select Printer'),
                                    fieldname: 'selected',
                                    fieldtype: 'Select',
                                    options: opts.join('\n'),
                                    description: __('Choose your printer to auto-fill the Vendor ID and Product ID')
                                }
                            ],
                            primary_action_label: __('Apply'),
                            primary_action: function(values) {
                                var sel_line = values.selected || '';
                                var idx = opts.indexOf(sel_line);
                                if (idx >= 0) {
                                    var p = printers[idx];
                                    frm.set_value('usb_vendor_id', p.vendor_id);
                                    frm.set_value('usb_product_id', p.product_id);
                                    frappe.show_alert({
                                        message: __('✓ Filled: ') + p.description,
                                        indicator: 'green'
                                    }, 4);
                                }
                                sel_dialog.hide();
                            }
                        });
                        sel_dialog.show();
                    }
                });
            }, __('USB Setup'));

            // ── Help section for USB ──────────────────────────────────────────
            frm.set_intro(
                __('<b>USB Printer Setup:</b> Click <b>Detect USB Printers</b> to auto-fill '
                + 'Vendor ID &amp; Product ID, or run <code>lsusb</code> on your server '
                + 'and enter the IDs manually (format: <code>0x04a9</code>).'),
                'blue'
            );

        } else if (ptype === 'Network (IP)') {
            frm.set_intro(
                __('<b>Network Printer:</b> Enter the printer\'s IP address and port (default 9100). '
                + 'Use <b>Test Connection</b> to verify reachability.'),
                'blue'
            );
        } else if (ptype === 'Email') {
            frm.set_intro(
                __('<b>Email Printer:</b> Documents will be emailed as PDF attachments to the recipients below.'),
                'blue'
            );
        } else if (ptype === 'PDF') {
            frm.set_intro(
                __('<b>PDF Printer:</b> Documents are generated as PDF files. '
                + 'Leave Save Path blank to download directly in the browser.'),
                'blue'
            );
        } else {
            frm.set_intro('');
        }
    }
});
