#!/usr/bin/env python3
"""Desktop window for the birthday gift message tool.

Run with: python3 gift_app.py   (or use the launcher in dist/)
"""

from __future__ import annotations

import threading

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk  # noqa: E402

import gift_logic as logic  # noqa: E402


class GiftApp(Gtk.Window):
    def __init__(self) -> None:
        super().__init__(title="Doğum Günü Hediyesi")
        self.set_default_size(560, 660)
        self.set_border_width(18)
        self.connect("delete-event", Gtk.main_quit)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.add(outer)

        title = Gtk.Label()
        title.set_markup("<b>Doğum günü hediye mesajı</b>")
        title.set_xalign(0)
        outer.pack_start(title, False, False, 0)

        subtitle = Gtk.Label(
            label="Tarih, ad, euro tutarı ve IBAN ile mesajı hazırla. TCMB kuru isterseniz API anahtarınızla alınır."
        )
        subtitle.set_xalign(0)
        subtitle.set_line_wrap(True)
        outer.pack_start(subtitle, False, False, 0)

        grid = Gtk.Grid()
        grid.set_row_spacing(9)
        grid.set_column_spacing(10)
        outer.pack_start(grid, False, False, 0)

        self.date_entry = self._add_entry(grid, 0, "Tarih (GG-AA-YYYY)", "Örn. 01-05-2024")
        calendar_button = Gtk.Button(label="Takvim")
        calendar_button.connect("clicked", self._open_calendar)
        grid.attach(calendar_button, 2, 0, 1, 1)

        self.name_entry = self._add_entry(grid, 1, "Ad", "Örn. Elif")
        self.amount_entry = self._add_entry(grid, 2, "Tutar (EUR)", "Örn. 25,50")
        self.iban_entry = self._add_entry(grid, 3, "IBAN", "TR00 0000 0000 0000 0000 0000 00")
        self.key_entry = self._add_entry(grid, 4, "EVDS anahtarı (isteğe bağlı)", "Anahtarınız varsa girin")
        self.key_entry.set_visibility(False)
        self.manual_entry = self._add_entry(grid, 5, "Kur elle (isteğe bağlı)", "Örn. 34,70 — internet yoksa")

        for entry in (
            self.date_entry,
            self.name_entry,
            self.amount_entry,
            self.iban_entry,
            self.key_entry,
            self.manual_entry,
        ):
            entry.connect("activate", self._generate)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.generate_button = Gtk.Button(label="Kuru al ve mesajı oluştur")
        self.generate_button.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
        self.generate_button.connect("clicked", self._generate)
        actions.pack_start(self.generate_button, False, False, 0)

        clear_button = Gtk.Button(label="Alanları temizle")
        clear_button.connect("clicked", self._clear)
        actions.pack_start(clear_button, False, False, 0)
        outer.pack_start(actions, False, False, 4)

        self.status = Gtk.Label(label="")
        self.status.set_xalign(0)
        self.status.set_line_wrap(True)
        outer.pack_start(self.status, False, False, 0)

        self.result = Gtk.Frame(label="Hazır mesaj")
        result_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        result_box.set_border_width(10)
        self.result.add(result_box)

        self.rate_label = Gtk.Label(label="Kur: –")
        self.rate_label.set_xalign(0)
        result_box.pack_start(self.rate_label, False, False, 0)

        self.total_label = Gtk.Label(label="TL tutarı: –")
        self.total_label.set_xalign(0)
        result_box.pack_start(self.total_label, False, False, 0)

        self.message_view = Gtk.TextView()
        self.message_view.set_editable(False)
        self.message_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.message_view.set_justification(Gtk.Justification.LEFT)
        scrolling = Gtk.ScrolledWindow()
        scrolling.set_min_content_height(90)
        scrolling.set_shadow_type(Gtk.ShadowType.IN)
        scrolling.add(self.message_view)
        result_box.pack_start(scrolling, True, True, 0)

        copy_button = Gtk.Button(label="Mesajı kopyala")
        copy_button.connect("clicked", self._copy)
        result_box.pack_start(copy_button, False, False, 0)
        self.result.hide()
        outer.pack_start(self.result, True, True, 0)

        footnote = Gtk.Label(
            label="Kur kaynağı: TCMB EVDS (anahtar girilirse), aksi halde ECB / Frankfurter. İnternet yoksa kur elle girilebilir."
        )
        footnote.set_xalign(0)
        footnote.set_line_wrap(True)
        outer.pack_start(footnote, False, False, 0)

    @staticmethod
    def _add_entry(grid: Gtk.Grid, row: int, label_text: str, placeholder: str) -> Gtk.Entry:
        label = Gtk.Label(label=label_text)
        label.set_xalign(0)
        grid.attach(label, 0, row, 1, 1)
        entry = Gtk.Entry()
        entry.set_placeholder_text(placeholder)
        entry.set_hexpand(True)
        grid.attach(entry, 1, row, 1, 1)
        return entry

    def _set_status(self, text: str, is_error: bool = False) -> None:
        self.status.set_text(text)
        style = self.status.get_style_context()
        if is_error:
            style.add_class("error")
        else:
            style.remove_class("error")

    def _open_calendar(self, _button: Gtk.Button) -> None:
        dialog = Gtk.Dialog(title="Tarih seç", parent=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Seç", Gtk.ResponseType.OK)
        calendar = Gtk.Calendar()
        dialog.get_content_area().pack_start(calendar, True, True, 8)
        dialog.show_all()
        if dialog.run() == Gtk.ResponseType.OK:
            year, month, day = calendar.get_date()
            self.date_entry.set_text(f"{day:02d}-{month + 1:02d}-{year:04d}")
        dialog.destroy()

    def _clear(self, _button: Gtk.Button) -> None:
        for entry in (
            self.date_entry,
            self.name_entry,
            self.amount_entry,
            self.iban_entry,
            self.key_entry,
            self.manual_entry,
        ):
            entry.set_text("")
        self.message_view.get_buffer().set_text("")
        self.result.hide()
        self._set_status("")

    def _generate(self, _button: Gtk.Button) -> None:
        name = self.name_entry.get_text().strip()
        iban = self.iban_entry.get_text().strip()
        try:
            date = logic.parse_date(self.date_entry.get_text())
            amount_eur = logic.parse_amount(self.amount_entry.get_text())
        except logic.GiftError as exc:
            self._set_status(str(exc), True)
            return
        if not name:
            self._set_status("Lütfen adı girin.", True)
            return

        self.generate_button.set_sensitive(False)
        self.result.hide()
        self._set_status("Kur alınıyor…")

        key = self.key_entry.get_text()
        manual = self.manual_entry.get_text()

        def work() -> None:
            try:
                info = logic.resolve_rate(date, evds_key=key, manual_rate=manual)
                GLib.idle_add(self._show_result, name, amount_eur, iban, info)
            except logic.GiftError as exc:
                message = f"{exc} Kur alanına TRY/EUR değerini elle yazabilirsiniz."
                GLib.idle_add(self._set_status, message, True)
            except Exception as exc:  # unexpected network/parsing failure
                GLib.idle_add(
                    self._set_status,
                    f"Beklenmeyen bir hata oluştu: {exc}",
                    True,
                )
            finally:
                GLib.idle_add(self.generate_button.set_sensitive, True)

        threading.Thread(target=work, daemon=True).start()

    def _show_result(self, name: str, amount_eur: float, iban: str, info: logic.RateInfo) -> bool:
        total = amount_eur * info.rate
        message = logic.build_message(name, total, iban)
        self.rate_label.set_text(f"Kur: {info.rate:.4f} TRY/EUR ({info.source}, {info.used_date})")
        self.total_label.set_text(f"TL tutarı: {logic.format_amount(total)} TL")
        self.message_view.get_buffer().set_text(message)
        note = f" {info.note}" if info.note else ""
        self._set_status("Mesaj hazır." + note)
        self.result.show()
        return False  # run once

    def _copy(self, _button: Gtk.Button) -> None:
        text = self.message_view.get_buffer().get_text()
        if not text:
            self._set_status("Önce mesajı oluşturun.", True)
            return
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(text, -1)
        clipboard.store()
        self._set_status("Mesaj kopyalandı.")


def main() -> None:
    css = b".error { color: #b00020; }"
    provider = Gtk.CssProvider()
    provider.load_from_data(css)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    window = GiftApp()
    window.show_all()
    window.result.hide()  # show_all would otherwise reveal the empty result frame
    Gtk.main()


if __name__ == "__main__":
    main()
