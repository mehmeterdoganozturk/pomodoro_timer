import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

PALETTE_COLORS = [
    ("#3B82F6", "Mavi"),
    ("#06B6D4", "Camgöbeği"),
    ("#10B981", "Yeşil"),
    ("#84CC16", "Açık Yeşil"),
    ("#F59E0B", "Amber"),
    ("#EF4444", "Kırmızı"),
    ("#EC4899", "Pembe"),
    ("#8B5CF6", "Mor")
]

QUICK_EMOJIS = ["📐", "📏", "🔬", "🧪", "📖", "💻", "⚡", "📚", "🏛️", "🧬", "📝", "🎯", "🎨"]

def open_subject_dialog(parent_window, storage, subject=None, on_saved=None):
    is_edit = subject is not None
    title = "Dersi Düzenle" if is_edit else "Yeni Ders Ekle"
    body = "Dersin adını, ikonunu ve rengini özelleştirin."

    dlg = Adw.AlertDialog.new(title, body)
    dlg.add_response("cancel", "İptal")
    dlg.add_response("save", "Kaydet" if is_edit else "Ekle")
    dlg.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)
    dlg.set_default_response("save")

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
    box.set_margin_top(10)
    box.set_margin_bottom(6)
    box.set_margin_start(12)
    box.set_margin_end(12)

    # 1. Ders Adı
    name_row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    lbl_name = Gtk.Label(label="Ders / Konu Adı")
    lbl_name.add_css_class("metric-sub")
    lbl_name.set_halign(Gtk.Align.START)
    name_entry = Gtk.Entry()
    name_entry.set_placeholder_text("Örn: Edebiyat, Tarih, Coğrafya...")
    if is_edit:
        name_entry.set_text(subject.get("name", ""))
    name_row.append(lbl_name)
    name_row.append(name_entry)
    box.append(name_row)

    # 2. İkon / Emoji
    icon_row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    lbl_icon = Gtk.Label(label="İkon (Emoji)")
    lbl_icon.add_css_class("metric-sub")
    lbl_icon.set_halign(Gtk.Align.START)
    icon_row.append(lbl_icon)

    # Quick Emoji Buttons
    emoji_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    emoji_box.set_halign(Gtk.Align.START)
    icon_entry = Gtk.Entry()
    icon_entry.set_max_length(4)
    icon_entry.set_width_chars(4)
    icon_entry.set_text(subject.get("icon", "📚") if is_edit else "📚")

    for em in QUICK_EMOJIS:
        btn = Gtk.Button(label=em)
        btn.add_css_class("flat")
        btn.connect("clicked", lambda b, e=em: icon_entry.set_text(e))
        emoji_box.append(btn)

    em_input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    em_input_box.append(icon_entry)
    em_input_box.append(emoji_box)
    icon_row.append(em_input_box)
    box.append(icon_row)

    # 3. Renk Seçimi
    color_row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    lbl_color = Gtk.Label(label="Tema Rengi")
    lbl_color.add_css_class("metric-sub")
    lbl_color.set_halign(Gtk.Align.START)
    color_row.append(lbl_color)

    selected_color = [subject.get("color", "#3B82F6") if is_edit else "#3B82F6"]
    color_buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

    color_btn_refs = []
    for hex_code, color_name in PALETTE_COLORS:
        c_btn = Gtk.Button()
        c_btn.set_tooltip_text(color_name)
        c_btn.set_size_request(28, 28)

        # Style with background color
        css = f"""
        button.color-btn-{hex_code.replace('#', '')} {{
            background-color: {hex_code};
            border-radius: 14px;
            border: 2px solid {'#FFFFFF' if hex_code == selected_color[0] else 'rgba(255,255,255,0.2)'};
        }}
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css.encode())
        c_btn.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        c_btn.add_css_class(f"color-btn-{hex_code.replace('#', '')}")

        def _make_color_click(hc, b):
            def _click(btn):
                selected_color[0] = hc
                # Update borders
                for other_btn, other_hc in color_btn_refs:
                    is_sel = (other_hc == hc)
                    up_css = f"""
                    button.color-btn-{other_hc.replace('#', '')} {{
                        background-color: {other_hc};
                        border-radius: 14px;
                        border: 2px solid {'#FFFFFF' if is_sel else 'rgba(255,255,255,0.2)'};
                    }}
                    """
                    p = Gtk.CssProvider()
                    p.load_from_data(up_css.encode())
                    other_btn.get_style_context().add_provider(p, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            return _click

        c_btn.connect("clicked", _make_color_click(hex_code, c_btn))
        color_btn_refs.append((c_btn, hex_code))
        color_buttons_box.append(c_btn)

    color_row.append(color_buttons_box)
    box.append(color_row)

    # 4. Ana Ekranda Göster (Görünürlük)
    vis_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_vis = Gtk.Label(label="Ana Sayaç Ekranında Göster")
    lbl_vis.add_css_class("discipline-title")
    vis_row.append(lbl_vis)

    spacer = Gtk.Box()
    spacer.set_hexpand(True)
    vis_row.append(spacer)

    vis_switch = Gtk.Switch()
    vis_switch.set_active(subject.get("visible", True) if is_edit else True)
    vis_row.append(vis_switch)
    box.append(vis_row)

    dlg.set_extra_child(box)

    def _on_response(dialog, result):
        resp = dialog.choose_finish(result)
        if resp == "save":
            name = name_entry.get_text().strip() or "Yeni Ders"
            icon = icon_entry.get_text().strip() or "📚"
            color = selected_color[0]
            visible = vis_switch.get_active()

            if is_edit:
                storage.update_subject(
                    subject["id"],
                    name=name,
                    icon=icon,
                    color=color,
                    badge=subject.get("badge", ""),
                    visible=visible
                )
            else:
                storage.add_subject(
                    name=name,
                    icon=icon,
                    color=color,
                    badge="Özel",
                    visible=visible
                )

            if on_saved:
                on_saved()

    dlg.choose(parent_window, None, _on_response)

def open_profile_dialog(parent_window, storage, on_saved=None):
    dlg = Adw.AlertDialog.new("Yeni Çalışma Modu / Profil", "Kendinize özel bir çalışma alanı oluşturun.")
    dlg.add_response("cancel", "İptal")
    dlg.add_response("save", "Oluştur")
    dlg.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)
    dlg.set_default_response("save")

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    box.set_margin_top(8)
    box.set_margin_bottom(6)
    box.set_margin_start(12)
    box.set_margin_end(12)

    # Profil Adı
    name_row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    lbl_name = Gtk.Label(label="Profil Adı")
    lbl_name.add_css_class("metric-sub")
    lbl_name.set_halign(Gtk.Align.START)
    name_entry = Gtk.Entry()
    name_entry.set_placeholder_text("Örn: 🎯 KPSS Hazırlık, 🇬🇧 İngilizce Öğrenme...")
    name_row.append(lbl_name)
    name_row.append(name_entry)
    box.append(name_row)

    # Açıklama
    desc_row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    lbl_desc = Gtk.Label(label="Açıklama / Hedef")
    lbl_desc.add_css_class("metric-sub")
    lbl_desc.set_halign(Gtk.Align.START)
    desc_entry = Gtk.Entry()
    desc_entry.set_placeholder_text("Örn: Genel Yetenek, Kelime Ezberi, Deneme...")
    desc_row.append(lbl_desc)
    desc_row.append(desc_entry)
    box.append(desc_row)

    # Odak Süresi & Mola Süresi
    times_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

    focus_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    lbl_f = Gtk.Label(label="Odak (dk)")
    lbl_f.add_css_class("metric-sub")
    spin_f = Gtk.SpinButton.new_with_range(10, 90, 5)
    spin_f.set_value(25)
    focus_box.append(lbl_f)
    focus_box.append(spin_f)
    times_row.append(focus_box)

    break_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    lbl_b = Gtk.Label(label="Kısa Mola (dk)")
    lbl_b.add_css_class("metric-sub")
    spin_b = Gtk.SpinButton.new_with_range(2, 30, 1)
    spin_b.set_value(5)
    break_box.append(lbl_b)
    break_box.append(spin_b)
    times_row.append(break_box)

    box.append(times_row)
    dlg.set_extra_child(box)

    def _on_response(dialog, result):
        resp = dialog.choose_finish(result)
        if resp == "save":
            name = name_entry.get_text().strip() or "Özel Mod"
            desc = desc_entry.get_text().strip() or "Özel Çalışma Alanı"
            focus_m = int(spin_f.get_value())
            break_m = int(spin_b.get_value())

            storage.create_profile(
                name=name,
                description=desc,
                default_focus=focus_m,
                default_break=break_m
            )

            if on_saved:
                on_saved()

    dlg.choose(parent_window, None, _on_response)

def confirm_delete_dialog(parent_window, title, body, on_confirmed):
    dlg = Adw.AlertDialog.new(title, body)
    dlg.add_response("cancel", "İptal")
    dlg.add_response("delete", "Sil")
    dlg.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
    dlg.set_default_response("cancel")

    def _on_response(dialog, result):
        resp = dialog.choose_finish(result)
        if resp == "delete" and on_confirmed:
            on_confirmed()

    dlg.choose(parent_window, None, _on_response)
