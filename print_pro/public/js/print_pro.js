/**
 * Print Pro - Core JS Controller
 * ERPNext v15 compatible
 * Provides: window.PrintPro  (global namespace)
 */

window.PrintPro = (function () {
    'use strict';

    const ICON_SVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="6 9 6 2 18 2 18 9"/>
        <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>
        <rect x="6" y="14" width="12" height="8"/>
    </svg>`;

    // ── Settings cache ────────────────────────────────────────────────────────
    let _settings = null;

    async function _getSettings() {
        if (_settings) return _settings;
        // Try boot session first
        if (frappe.boot && frappe.boot.print_pro) {
            _settings = frappe.boot.print_pro;
        } else {
            const r = await frappe.call({ method: 'print_pro.api.get_settings' });
            _settings = r.message || {};
        }
        return _settings;
    }

    // ── Main entry point ──────────────────────────────────────────────────────
    async function openDialog(doctype, docname) {
        const settings = await _getSettings();
        if (!settings.enabled) return;

        // Fetch all needed data
        frappe.show_progress(__('Loading...'), 50, 100, __('Preparing Print Pro...'));
        let data;
        try {
            const r = await frappe.call({
                method: 'print_pro.api.get_print_dialog_data',
                args: { doctype, docname },
            });
            data = r.message;
        } catch (e) {
            frappe.hide_progress();
            frappe.show_alert({ message: __('Failed to load print options.'), indicator: 'red' });
            return;
        }
        frappe.hide_progress();

        _showPrintDialog(doctype, docname, data, settings);
    }

    // ── Dialog builder ────────────────────────────────────────────────────────
    function _showPrintDialog(doctype, docname, data, settings) {
        const { pro_formats, native_formats, printers, doc_info } = data;
        const s = data.settings;

        // Build format options
        const fmtOptions = [];
        if (pro_formats && pro_formats.length) {
            pro_formats.forEach(f => {
                fmtOptions.push({
                    label: `★ ${f.format_name}`,
                    value: `pp::${f.name}`,
                    default: !!f.is_default,
                });
            });
        }
        if (native_formats && native_formats.length) {
            native_formats.forEach(f => {
                fmtOptions.push({
                    label: `${f.name} (ERPNext)`,
                    value: `native::${f.name}`,
                });
            });
        }
        if (!fmtOptions.length) {
            fmtOptions.push({ label: __('Standard'), value: 'native::Standard' });
        }

        // Build printer options
        const printerOptions = [{ label: __('-- Auto Select --'), value: '' }];
        if (printers && printers.length) {
            printers.forEach(p => {
                printerOptions.push({
                    label: `${p.printer_name} (${p.printer_type})${p.is_default ? ' ★' : ''}`,
                    value: p.name,
                });
            });
        }

        const dialog = new frappe.ui.Dialog({
            title: `<span style="display:flex;align-items:center;gap:8px;">
                ${ICON_SVG} ${__('Print Pro')} — ${docname}
                <span class="pp-shortcut-badge">Ctrl+P</span>
            </span>`,
            size: 'large',
            fields: [
                {
                    fieldname: 'print_format',
                    fieldtype: 'Select',
                    label: __('Print Format'),
                    options: fmtOptions.map(o => o.label).join('\n'),
                    default: (fmtOptions.find(f => f.default) || fmtOptions[0]).label,
                },
                {
                    fieldname: 'col1',
                    fieldtype: 'Column Break',
                },
                {
                    fieldname: 'printer',
                    fieldtype: 'Select',
                    label: __('Printer'),
                    options: printerOptions.map(o => o.label).join('\n'),
                },
                {
                    fieldname: 'sb1',
                    fieldtype: 'Section Break',
                    label: __('Page Settings'),
                },
                {
                    fieldname: 'paper_size',
                    fieldtype: 'Select',
                    label: __('Paper Size'),
                    options: 'A4\nA5\nA3\nLetter\nLegal\nThermal 80mm\nThermal 58mm',
                    default: s.default_paper_size || 'A4',
                },
                {
                    fieldname: 'col2',
                    fieldtype: 'Column Break',
                },
                {
                    fieldname: 'orientation',
                    fieldtype: 'Select',
                    label: __('Orientation'),
                    options: 'Portrait\nLandscape',
                    default: s.default_orientation || 'Portrait',
                },
                {
                    fieldname: 'col3',
                    fieldtype: 'Column Break',
                },
                {
                    fieldname: 'copies',
                    fieldtype: 'Int',
                    label: __('Copies'),
                    default: 1,
                },
                {
                    fieldname: 'sb2',
                    fieldtype: 'Section Break',
                    label: __('Print History'),
                },
                {
                    fieldname: 'print_log_html',
                    fieldtype: 'HTML',
                    label: '',
                },
            ],
            primary_action_label: `${ICON_SVG} ${__('Print')}`,
            primary_action(values) {
                _executePrint(doctype, docname, values, fmtOptions, printerOptions, dialog);
            },
            secondary_action_label: __('Download PDF'),
            secondary_action(values) {
                _downloadPDF(doctype, docname, values, fmtOptions);
                dialog.hide();
            },
        });

        // Custom header style
        dialog.$wrapper.find('.modal-header').addClass('print-pro-dialog');
        dialog.$wrapper.addClass('print-pro-dialog');

        // Load print log async
        _loadPrintLog(dialog, doctype, docname);

        // Add Preview button
        dialog.add_custom_action(__('Preview'), () => {
            const values = dialog.get_values();
            _previewDoc(doctype, docname, values, fmtOptions);
        });

        dialog.show();

        // Keyboard shortcut: Ctrl+Enter to print
        dialog.$wrapper.on('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                dialog.get_primary_btn().click();
            }
        });
    }

    // ── Print execution ───────────────────────────────────────────────────────
    async function _executePrint(doctype, docname, values, fmtOptions, printerOptions, dialog) {
        const { printer: printerLabel, print_format: fmtLabel, paper_size, orientation, copies } = values;

        // Resolve printer value
        const printerEntry = printerOptions.find(p => p.label === printerLabel);
        const printerVal = printerEntry ? printerEntry.value : '';

        // Resolve format
        const { ppFmt, nativeFmt } = _resolveFormat(fmtLabel, fmtOptions);

        frappe.show_progress(__('Printing...'), 60, 100);

        const r = await frappe.call({
            method: 'print_pro.api.print_document',
            args: {
                doctype,
                docname,
                printer: printerVal,
                print_format: ppFmt,
                copies: copies || 1,
                paper_size,
                orientation,
                use_native_format: nativeFmt,
            },
        });

        frappe.hide_progress();

        if (r.message && r.message.success) {
            frappe.show_alert({ message: __('✓ Print job sent successfully!'), indicator: 'green' }, 4);
            dialog.hide();
        } else {
            frappe.show_alert({
                message: __('Print failed: ') + (r.message && r.message.message || __('Unknown error')),
                indicator: 'red',
            }, 6);
        }
    }

    // ── PDF Download ──────────────────────────────────────────────────────────
    function _downloadPDF(doctype, docname, values, fmtOptions) {
        const { ppFmt, nativeFmt } = _resolveFormat(values.print_format, fmtOptions);
        const url = `/api/method/print_pro.api.get_pdf_for_download?doctype=${encodeURIComponent(doctype)}&docname=${encodeURIComponent(docname)}&print_format=${ppFmt || ''}&use_native_format=${nativeFmt || ''}`;
        window.open(url, '_blank');
    }

    // ── Preview ───────────────────────────────────────────────────────────────
    function _previewDoc(doctype, docname, values, fmtOptions) {
        const { ppFmt, nativeFmt } = _resolveFormat(values.print_format, fmtOptions);
        const url = `/api/method/print_pro.api.preview_format?doctype=${encodeURIComponent(doctype)}&name=${encodeURIComponent(docname)}&format=${ppFmt || ''}&use_native=${nativeFmt || ''}`;
        window.open(url, '_blank');
    }

    // ── Print Log ─────────────────────────────────────────────────────────────
    async function _loadPrintLog(dialog, doctype, docname) {
        try {
            const r = await frappe.call({
                method: 'print_pro.api.get_print_log',
                args: { doctype, docname },
            });
            const logs = r.message || [];
            if (!logs.length) {
                dialog.fields_dict.print_log_html.$wrapper.html(
                    `<p style="color:#6c757d;font-size:12px;text-align:center;padding:8px;">${__('No print history yet.')}</p>`
                );
                return;
            }
            const rows = logs.map(l => `
                <tr>
                    <td>${frappe.datetime.str_to_user(l.printed_on)}</td>
                    <td>${l.printed_by || '-'}</td>
                    <td>${l.printer || '-'}</td>
                    <td>${l.print_format || '-'}</td>
                    <td>${l.copies || 1}</td>
                    <td><span class="pp-status-badge ${(l.status || '').toLowerCase()}">${l.status}</span></td>
                </tr>`).join('');
            dialog.fields_dict.print_log_html.$wrapper.html(`
                <table class="pp-log-table">
                    <thead><tr>
                        <th>${__('Date')}</th><th>${__('By')}</th>
                        <th>${__('Printer')}</th><th>${__('Format')}</th>
                        <th>${__('Copies')}</th><th>${__('Status')}</th>
                    </tr></thead>
                    <tbody>${rows}</tbody>
                </table>`);
        } catch (e) { /* silently fail */ }
    }

    // ── Format resolver ───────────────────────────────────────────────────────
    function _resolveFormat(label, fmtOptions) {
        const entry = fmtOptions.find(f => f.label === label);
        if (!entry) return { ppFmt: null, nativeFmt: null };
        if (entry.value.startsWith('pp::')) return { ppFmt: entry.value.slice(4), nativeFmt: null };
        if (entry.value.startsWith('native::')) return { ppFmt: null, nativeFmt: entry.value.slice(8) };
        return { ppFmt: null, nativeFmt: null };
    }

    // ── Inject button into a form ─────────────────────────────────────────────
    function injectButton(frm) {
        if (!frm || !frm.doctype || !frm.docname) return;
        // Don't add if already added
        if (frm._printProButtonAdded) return;

        _getSettings().then(settings => {
            if (!settings.enabled || !settings.show_print_pro_button) return;

            frm.add_custom_button(
                `${ICON_SVG} ${__('Print Pro')}`,
                () => openDialog(frm.doctype, frm.docname),
                __('Print')
            );
            frm._printProButtonAdded = true;

            // Optionally hide default print button
            if (settings.replace_default_print) {
                frm.page.btn_secondary && frm.page.btn_secondary.find('[data-label="Print"]').hide();
            }
        });
    }

    // ── Keyboard shortcut (global Ctrl+Shift+P) ───────────────────────────────
    $(document).on('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'P') {
            e.preventDefault();
            const frm = cur_frm;
            if (frm && frm.doctype && frm.docname) {
                openDialog(frm.doctype, frm.docname);
            }
        }
    });

    // ── Public API ────────────────────────────────────────────────────────────
    return {
        openDialog,
        injectButton,
        version: '1.0.0',
    };

})();

// Auto-inject on route change for supported doctypes
frappe.router.on('change', () => {
    if (cur_frm) {
        PrintPro.injectButton(cur_frm);
    }
});
