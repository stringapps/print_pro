// Print Pro — Quotation override  (v3 helper)
// Auto-generated.

// ─── Print Pro shared helper (v3) ────────────────────────────────────────────
// Guard: only first-loaded override defines this; all others reuse it.
if (!window._PrintProForm) {
    window._PrintProForm = {

        // ── Add the "🖨 Print Pro" button under the Print menu ───────────────
        injectButton: function(frm) {
            if (frm.is_new() || frm._pp_btn_added) return;
            frm._pp_btn_added = true;
            var btn = frm.add_custom_button(
                '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" '
                + 'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
                + '<polyline points="6 9 6 2 18 2 18 9"/>'
                + '<path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>'
                + '<rect x="6" y="14" width="12" height="8"/></svg> ' + __('Print Pro'),
                function() { window._PrintProForm.openDialog(frm.doctype, frm.docname); },
                __('Print')
            );
            if (btn && btn.length) {
                btn.css({ background: '#1a73e8', color: '#fff', border: 'none', 'font-weight': '600' });
            }
        },

        // ── Resolve format value from label ─────────────────────────────────
        _resolveFmt: function(fmt_opts, label) {
            var sel = fmt_opts.find(function(f) { return f.label === label; });
            if (!sel) return { pp: '', native: '' };
            var pp = '', native = '';
            if (sel.value.indexOf('pp::') === 0)          pp     = sel.value.slice(4);
            else if (sel.value.indexOf('native::') === 0)  native = sel.value.slice(8);
            return { pp: pp, native: native };
        },

        // ── Show error state in preview wrap ────────────────────────────────
        _previewError: function(msg) {
            var wrap = document.getElementById('pp-preview-wrap');
            if (!wrap) return;
            wrap.style.cssText = 'min-height:120px;border:1px solid #fecaca;border-radius:8px;'
                + 'background:#fff5f5;display:flex;align-items:center;justify-content:center;padding:16px;';
            wrap.innerHTML = '<div style="color:#ef4444;font-size:11px;line-height:1.5;">'
                + '<strong style="display:block;margin-bottom:4px;">⚠ Preview Error</strong>'
                + '<span style="word-break:break-word;">' + (msg || 'Unknown error') + '</span>'
                + '<br><span style="color:#888;font-size:10px;">Fix the template error, then click Preview again.</span>'
                + '</div>';
        },

        // ── Load preview into the iframe ─────────────────────────────────────
        _loadPreview: function(dialog, doctype, docname, fmt_opts) {
            var values = dialog.get_values();
            var fmt = window._PrintProForm._resolveFmt(fmt_opts, values.print_format);
            var wrap = document.getElementById('pp-preview-wrap');
            if (!wrap) return;

            // Reset to loading state every time (clears stale error or old iframe)
            wrap.style.cssText = 'min-height:420px;border:1px solid #e2e8f0;border-radius:8px;'
                + 'background:#f8fafc;display:flex;align-items:center;justify-content:center;';
            wrap.innerHTML = '<div style="text-align:center;color:#64748b;padding:40px;">'
                + '<div style="font-size:12px;font-weight:500;">⏳ Loading preview…</div>'
                + '</div>';

            frappe.call({
                method: 'print_pro.api.preview_format',
                args: {
                    doctype: doctype, name: docname,
                    format: fmt.pp, use_native: fmt.native,
                    paper_size: values.paper_size   || 'A4',
                    orientation: values.orientation || 'Portrait'
                },
                callback: function(r) {
                    var wrap2 = document.getElementById('pp-preview-wrap');
                    if (!wrap2) return;
                    if (r.message && r.message.html) {
                        var iframe = document.createElement('iframe');
                        iframe.style.cssText = 'width:100%;height:540px;border:none;border-radius:6px;'
                            + 'background:#fff;display:block;';
                        wrap2.style.cssText = 'background:#fff;border:1px solid #e2e8f0;'
                            + 'border-radius:6px;overflow:hidden;';
                        wrap2.innerHTML = '';
                        wrap2.appendChild(iframe);
                        iframe.srcdoc = r.message.html;
                    } else {
                        var errMsg = (r.message && r.message.error) || 'Preview failed. Check template.';
                        window._PrintProForm._previewError(errMsg);
                    }
                },
                // FIX: handle server-side exceptions (Jinja errors, etc.)
                error: function(r) {
                    var errMsg = 'Server error';
                    if (r && r.message) errMsg = r.message;
                    else if (typeof r === 'string') errMsg = r;
                    window._PrintProForm._previewError(errMsg);
                }
            });
        },

        // ── Open guard ───────────────────────────────────────────────────────
        // BUG FIX: removed 800ms setTimeout — it caused a 2nd dialog to open
        openDialog: function(doctype, docname) {
            if (window._pp_dialog_opening) return;
            window._pp_dialog_opening = true;

            frappe.call({
                method: 'print_pro.api.get_print_dialog_data',
                args: { doctype: doctype, docname: docname },
                callback: function(r) {
                    window._pp_dialog_opening = false;
                    if (!r.message) return;
                    window._PrintProForm._simplePrintDialog(doctype, docname, r.message);
                },
                error: function() {
                    window._pp_dialog_opening = false;
                    frappe.show_alert({ message: __('Failed to load print options.'), indicator: 'red' }, 5);
                }
            });
        },

        // ── Build and show the print dialog ──────────────────────────────────
        _simplePrintDialog: function(doctype, docname, data) {
            // Guard: prevent opening twice from the same trigger
            if (window._pp_dialog_open) return;
            window._pp_dialog_open = true;

            var s            = data.settings || {};
            var pro_fmts     = data.pro_formats   || [];
            var native_fmts  = data.native_formats || [];
            var printers     = data.printers       || [];

            // ── Build format options list ─────────────────────────────────────
            var fmt_opts = [];
            pro_fmts.forEach(function(f) {
                fmt_opts.push({ label: '★ ' + f.format_name, value: 'pp::' + f.name });
            });
            native_fmts.forEach(function(f) {
                fmt_opts.push({ label: f.name + '  (ERPNext)', value: 'native::' + f.name });
            });
            if (!fmt_opts.length) fmt_opts.push({ label: '— Default —', value: '' });

            var def_fmt = fmt_opts[0].label;
            // Prefer the default-flagged Pro format
            var defPro = pro_fmts.find(function(f) { return f.is_default; });
            if (defPro) def_fmt = '★ ' + defPro.format_name;

            // ── Printer options ───────────────────────────────────────────────
            var prt_opts = [{ label: '— Default Printer —', value: '' }];
            printers.forEach(function(p) {
                prt_opts.push({ label: p.printer_name + '  (' + (p.printer_type || '') + ')', value: p.name });
            });

            // ── Declare dialog FIRST (needed for onchange closure below) ──────
            var dialog;

            dialog = new frappe.ui.Dialog({
                title: '🖨 Print Pro — ' + docname,
                fields: [
                    { fieldname: 'sb_fmt', fieldtype: 'Section Break', label: __('Format & Printer') },
                    {
                        label: __('Print Format'), fieldname: 'print_format',
                        fieldtype: 'Select',
                        options: fmt_opts.map(function(o) { return o.label; }).join('\n'),
                        default: def_fmt,
                        description: __('★ = Print Pro formats  |  (ERPNext) = native ERPNext formats'),
                        // FIX: auto-refresh preview when format changes
                        onchange: function() {
                            if (!dialog) return;
                            var wrap = document.getElementById('pp-preview-wrap');
                            // Only auto-refresh if preview was already loaded (has an iframe)
                            if (wrap && wrap.querySelector('iframe')) {
                                window._PrintProForm._loadPreview(dialog, doctype, docname, fmt_opts);
                            }
                        }
                    },
                    { fieldname: 'cb1', fieldtype: 'Column Break' },
                    {
                        label: __('Printer'), fieldname: 'printer',
                        fieldtype: 'Select',
                        options: prt_opts.map(function(o) { return o.label; }).join('\n'),
                        description: __('Leave blank to use the default printer')
                    },
                    { fieldname: 'sb_page', fieldtype: 'Section Break', label: __('Page Settings') },
                    {
                        label: __('Paper Size'), fieldname: 'paper_size',
                        fieldtype: 'Select',
                        options: ['A4', 'A5', 'Letter', 'Legal', 'Thermal 80mm', 'Thermal 58mm', 'Custom'].join('\n'),
                        default: s.default_paper_size || 'A4'
                    },
                    { fieldname: 'cb2', fieldtype: 'Column Break' },
                    {
                        label: __('Orientation'), fieldname: 'orientation',
                        fieldtype: 'Select',
                        options: ['Portrait', 'Landscape'].join('\n'),
                        default: s.default_orientation || 'Portrait'
                    },
                    { fieldname: 'sb_copies', fieldtype: 'Section Break', label: __('Copies') },
                    {
                        label: __('Copies'), fieldname: 'copies',
                        fieldtype: 'Int', default: 1
                    },
                    { fieldname: 'cb3', fieldtype: 'Column Break' },
                    {
                        label: __('With Letterhead'), fieldname: 'with_letterhead',
                        fieldtype: 'Check', default: 1
                    },
                    // ── Preview area ─────────────────────────────────────────
                    { fieldname: 'sb_preview', fieldtype: 'Section Break', label: __('Preview') },
                    {
                        fieldname: 'preview_html', fieldtype: 'HTML',
                        options: '<div id="pp-preview-wrap" style="min-height:420px;border:1px solid #e2e8f0;'
                            + 'border-radius:8px;background:#f8fafc;display:flex;align-items:center;'
                            + 'justify-content:center;">'
                            + '<div style="text-align:center;color:#94a3b8;padding:40px;">'
                            + '<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" fill="none" '
                            + 'stroke="#94a3b8" stroke-width="1.5" viewBox="0 0 24 24">'
                            + '<polyline points="6 9 6 2 18 2 18 9"/>'
                            + '<path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>'
                            + '<rect x="6" y="14" width="12" height="8"/></svg>'
                            + '<div style="margin-top:10px;font-size:12px;font-weight:500;">Click <b>Preview</b> to see document</div>'
                            + '</div></div>'
                    }
                ],
                primary_action_label: __('🖨  Print'),
                primary_action: function(values) {
                    var fmt = window._PrintProForm._resolveFmt(fmt_opts, values.print_format);
                    var prt = (values.printer && prt_opts.find(function(p) {
                        return p.label === values.printer;
                    }));
                    frappe.call({
                        method: 'print_pro.api.print_document',
                        args: {
                            doctype: doctype,
                            docname: docname,
                            printer: prt ? prt.value : '',
                            print_format: fmt.pp,
                            use_native_format: fmt.native,
                            copies: values.copies || 1,
                            paper_size: values.paper_size   || 'A4',
                            orientation: values.orientation || 'Portrait'
                        },
                        freeze: true, freeze_message: __('Sending print job…'),
                        callback: function(r) {
                            if (r.message && r.message.success) {
                                frappe.show_alert({ message: __('✓ Print job sent!'), indicator: 'green' }, 5);
                                var res = r.message.result || {};
                                if (res.type === 'download' && res.file_url) {
                                    setTimeout(function() {
                                        var a = document.createElement('a');
                                        a.href = res.file_url;
                                        a.target = '_blank';
                                        a.download = docname + '.pdf';
                                        document.body.appendChild(a);
                                        a.click();
                                        document.body.removeChild(a);
                                    }, 300);
                                }
                                dialog.hide();
                            } else {
                                var err = (r.message && r.message.message) || __('Unknown error');
                                frappe.show_alert({ message: __('✗ Print failed: ') + err, indicator: 'red' }, 8);
                            }
                        },
                        error: function() {
                            frappe.show_alert({ message: __('✗ Print request failed.'), indicator: 'red' }, 8);
                        }
                    });
                },
                onhide: function() {
                    // Reset guard so button can be clicked again
                    window._pp_dialog_open    = false;
                    window._pp_dialog_opening = false;
                }
            });

            // ── Custom action buttons ─────────────────────────────────────────
            dialog.add_custom_action(__('👁  Preview'), function() {
                window._PrintProForm._loadPreview(dialog, doctype, docname, fmt_opts);
            }, 'btn-default');

            dialog.add_custom_action(__('⬇  Download PDF'), function() {
                var values = dialog.get_values();
                var fmt = window._PrintProForm._resolveFmt(fmt_opts, values.print_format);
                var params = new URLSearchParams({
                    doctype: doctype, docname: docname,
                    print_format: fmt.pp,
                    use_native_format: fmt.native,
                    paper_size: values.paper_size   || 'A4',
                    orientation: values.orientation || 'Portrait'
                });
                var a = document.createElement('a');
                a.href = '/api/method/print_pro.api.get_pdf_for_download?' + params.toString();
                a.target = '_blank';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            }, 'btn-default');

            dialog.show();

            // Auto-load preview if settings say to show it on open
            if (s.show_preview) {
                setTimeout(function() {
                    window._PrintProForm._loadPreview(dialog, doctype, docname, fmt_opts);
                }, 200);
            }
        }
    };
}
// ─────────────────────────────────────────────────────────────────────────────

frappe.ui.form.on('Quotation', {
    refresh: function(frm) {
        if (!frm.is_new()) { window._PrintProForm.injectButton(frm); }
    }
});
