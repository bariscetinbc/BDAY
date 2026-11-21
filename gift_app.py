#!/usr/bin/env python3
"""Desktop window for BDAY (Linux/GTK 3).

Run with: python3 gift_app.py   (or use the launcher in dist/)
Currency, language and light/dark theme can all be changed in the window and
are remembered between runs.
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
        self.prefs = logic.load_preferences()
        self.lang = self.prefs["lang"]
        self.theme = self.prefs["theme"]
        self.currency = self.prefs["currency"]
        self.evds_key = self.prefs.get("evds_key", "")
        self.last_result = None

        super().__init__(title="BDAY")
        self.get_style_context().add_class("gift-window")
        self.set_default_size(600, 720)
        self.set_border_width(18)
        self.connect("delete-event", Gtk.main_quit)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.add(outer)

        self.title = Gtk.Label()
        self.title.set_xalign(0)
        outer.pack_start(self.title, False, False, 0)

        self.subtitle = Gtk.Label()
        self.subtitle.set_xalign(0)
        self.subtitle.set_line_wrap(True)
        outer.pack_start(self.subtitle, False, False, 0)

        # Preferences: currency, language and theme.
        prefs_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.prefs_frame = Gtk.Frame(label=self.tr("preferences"))
        prefs_frame = self.prefs_frame
        prefs_inner = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        prefs_inner.set_border_width(10)
        prefs_frame.add(prefs_inner)

        self.currency_label = Gtk.Label()
        self.currency_combo = Gtk.ComboBoxText()
        for code in logic.CURRENCIES:
            self.currency_combo.append_text(code)
        self.currency_combo.set_active(list(logic.CURRENCIES).index(self.currency))
        self.currency_combo.connect("changed", self._currency_changed)
        prefs_inner.pack_start(self.currency_label, False, False, 0)
        prefs_inner.pack_start(self.currency_combo, False, False, 0)

        self.language_label = Gtk.Label()
        self.language_combo = Gtk.ComboBoxText()
        self.language_combo.append_text("Türkçe")
        self.language_combo.append_text("English")
        self.language_combo.set_active(0 if self.lang == "tr" else 1)
        self.language_combo.connect("changed", self._language_changed)
        prefs_inner.pack_start(self.language_label, False, False, 0)
        prefs_inner.pack_start(self.language_combo, False, False, 0)

        self.theme_button = Gtk.Button()
        self.theme_button.connect("clicked", self._theme_toggled)
        prefs_inner.pack_start(self.theme_button, False, False, 0)
        prefs_box.pack_start(prefs_frame, False, False, 0)
        outer.pack_start(prefs_box, False, False, 0)

        grid = Gtk.Grid()
        grid.set_row_spacing(9)
        grid.set_column_spacing(10)
        outer.pack_start(grid, False, False, 0)

        self.date_label = Gtk.Label()
        self.date_label.set_xalign(0)
        grid.attach(self.date_label, 0, 0, 1, 1)
        self.date_entry = Gtk.Entry()
        self.date_entry.set_hexpand(True)
        grid.attach(self.date_entry, 1, 0, 1, 1)
        self.calendar_button = Gtk.Button()
        self.calendar_button.connect("clicked", self._open_calendar)
        grid.attach(self.calendar_button, 2, 0, 1, 1)

        self.name_label = Gtk.Label()
        self.name_label.set_xalign(0)
        grid.attach(self.name_label, 0, 1, 1, 1)
        self.name_entry = Gtk.Entry()
        self.name_entry.set_hexpand(True)
        grid.attach(self.name_entry, 1, 1, 1, 1)

        self.amount_label = Gtk.Label()
        self.amount_label.set_xalign(0)
        grid.attach(self.amount_label, 0, 2, 1, 1)
        self.amount_entry = Gtk.Entry()
        self.amount_entry.set_hexpand(True)
        grid.attach(self.amount_entry, 1, 2, 1, 1)

        self.iban_label = Gtk.Label()
        self.iban_label.set_xalign(0)
        grid.attach(self.iban_label, 0, 3, 1, 1)
        self.iban_entry = Gtk.Entry()
        self.iban_entry.set_hexpand(True)
        grid.attach(self.iban_entry, 1, 3, 1, 1)

        self.key_label = Gtk.Label()
        self.key_label.set_xalign(0)
        grid.attach(self.key_label, 0, 4, 1, 1)
        self.key_entry = Gtk.Entry()
        self.key_entry.set_visibility(False)
        self.key_entry.set_hexpand(True)
        grid.attach(self.key_entry, 1, 4, 1, 1)
        self.forget_key_button = Gtk.Button()
        self.forget_key_button.connect("clicked", self._forget_key)
        grid.attach(self.forget_key_button, 2, 4, 1, 1)
        self.key_entry.set_text(self.evds_key)
        self.key_entry.connect("changed", self._key_changed)

        self.manual_label = Gtk.Label()
        self.manual_label.set_xalign(0)
        grid.attach(self.manual_label, 0, 5, 1, 1)
        self.manual_entry = Gtk.Entry()
        self.manual_entry.set_hexpand(True)
        grid.attach(self.manual_entry, 1, 5, 1, 1)

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
        self.generate_button = Gtk.Button()
        self.generate_button.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
        self.generate_button.connect("clicked", self._generate)
        actions.pack_start(self.generate_button, False, False, 0)
        self.clear_button = Gtk.Button()
        self.clear_button.connect("clicked", self._clear)
        actions.pack_start(self.clear_button, False, False, 0)
        outer.pack_start(actions, False, False, 4)

        self.status = Gtk.Label(label="")
        self.status.set_xalign(0)
        self.status.set_line_wrap(True)
        outer.pack_start(self.status, False, False, 0)

        self.result = Gtk.Frame()
        result_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        result_box.set_border_width(10)
        self.result.add(result_box)

        self.rate_label = Gtk.Label()
        self.rate_label.set_xalign(0)
        result_box.pack_start(self.rate_label, False, False, 0)

        self.total_label = Gtk.Label()
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

        self.copy_button = Gtk.Button()
        self.copy_button.connect("clicked", self._copy)
        result_box.pack_start(self.copy_button, False, False, 0)
        outer.pack_start(self.result, True, True, 0)

        self.footnote = Gtk.Label()
        self.footnote.set_xalign(0)
        self.footnote.set_line_wrap(True)
        outer.pack_start(self.footnote, False, False, 0)

        self._retranslate()
        self._apply_theme()
        self.result.hide()

    def tr(self, key: str, **variables) -> str:
        return logic.t(self.lang, key, **variables)

    def _apply_theme(self) -> None:
        dark = self.theme == "dark"
        settings = Gtk.Settings.get_default()
        if settings is not None:
            settings.set_property("gtk-application-prefer-dark-theme", dark)
        provider = Gtk.CssProvider()
        if dark:
            css = (
                ".gift-window { background-color: #202328; color: #eef1f5; } "
                ".error { color: #ff8a9c; }"
            )
        else:
            css = (
                ".gift-window { background-color: #ffffff; color: #000000; } "
                ".error { color: #b00020; }"
            )
        provider.load_from_data(css.encode("utf-8"))
        screen = Gdk.Screen.get_default()
        if screen is not None:
            Gtk.StyleContext.add_provider_for_screen(
                screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def _save_preferences(self) -> None:
        logic.save_preferences(
            {
                "lang": self.lang,
                "theme": self.theme,
                "currency": self.currency,
                "evds_key": self.evds_key,
            }
        )

    def _key_changed(self, _entry: Gtk.Entry) -> None:
        self.evds_key = self.key_entry.get_text().strip()
        self._update_key_controls()
        self._save_preferences()

    def _update_key_controls(self) -> None:
        self.forget_key_button.set_sensitive(bool(self.evds_key))
        self.key_entry.set_tooltip_text(self.tr("keyRestored") if self.evds_key else "")

    def _forget_key(self, _button: Gtk.Button) -> None:
        self.evds_key = ""
        self.key_entry.set_text("")
        self._update_key_controls()
        self._save_preferences()
        self._set_status(self.tr("keyForgotten"))

    def _retranslate(self) -> None:
        self.set_title("BDAY — " + self.tr("title"))
        self.title.set_markup("<b>" + self.tr("title") + "</b>")
        self.subtitle.set_text(self.tr("subtitle"))
        self.prefs_frame.set_label(self.tr("preferences"))
        self.currency_label.set_text(self.tr("currency"))
        self.language_label.set_text(self.tr("language"))
        self.theme_button.set_label(self.tr("themeDark") if self.theme == "light" else self.tr("themeLight"))
        self.date_label.set_text(self.tr("date"))
        self.date_entry.set_placeholder_text(self.tr("datePlaceholder"))
        self.calendar_button.set_label(self.tr("calendar"))
        self.name_label.set_text(self.tr("name"))
        self.name_entry.set_placeholder_text(self.tr("namePlaceholder"))
        self.amount_label.set_text(self.tr("amount") + " (" + self.currency + ")")
        self.amount_entry.set_placeholder_text(self.tr("amountPlaceholder"))
        self.iban_label.set_text(self.tr("iban"))
        self.iban_entry.set_placeholder_text(self.tr("ibanPlaceholder"))
        self.key_label.set_text(self.tr("key"))
        self.key_entry.set_placeholder_text(self.tr("keyPlaceholder"))
        self.manual_label.set_text(self.tr("manual", currency=self.currency))
        self.manual_entry.set_placeholder_text(self.tr("manualPlaceholder"))
        self.generate_button.set_label(self.tr("generate"))
        self.clear_button.set_label(self.tr("clear"))
        self.result.set_label(self.tr("result"))
        self.copy_button.set_label(self.tr("copy"))
        self.forget_key_button.set_label(self.tr("forgetKey"))
        self.footnote.set_text(self.tr("footnote"))
        self._update_key_controls()

    def _currency_changed(self, _combo: Gtk.ComboBoxText) -> None:
        code = self.currency_combo.get_active_text()
        if not code or code == self.currency:
            return
        self.currency = code
        self.last_result = None
        self.result.hide()
        self._retranslate()
        self._save_preferences()

    def _language_changed(self, _combo: Gtk.ComboBoxText) -> None:
        self.lang = "tr" if self.language_combo.get_active() == 0 else "en"
        self._retranslate()
        if self.last_result:
            info, name, amount, iban = self.last_result
            self._show_result(info, name, amount, iban)
        self._save_preferences()

    def _theme_toggled(self, _button: Gtk.Button) -> None:
        self.theme = "dark" if self.theme == "light" else "light"
        self._apply_theme()
        self._retranslate()
        self._save_preferences()

    def _set_status(self, text: str, is_error: bool = False) -> None:
        self.status.set_text(text)
        style = self.status.get_style_context()
        if is_error:
            style.add_class("error")
        else:
            style.remove_class("error")

    def _open_calendar(self, _button: Gtk.Button) -> None:
        dialog = Gtk.Dialog(title=self.tr("selectDate"), parent=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, self.tr("select"), Gtk.ResponseType.OK)
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
            self.manual_entry,
        ):
            entry.set_text("")
        self.key_entry.set_text(self.evds_key)  # a saved key is a preference, not form data
        self.message_view.get_buffer().set_text("")
        self.result.hide()
        self.last_result = None
        self._set_status("")

    def _generate(self, _button: Gtk.Button) -> None:
        name = self.name_entry.get_text().strip()
        iban = self.iban_entry.get_text().strip()
        try:
            date = logic.parse_date(self.date_entry.get_text())
            amount = logic.parse_amount(self.amount_entry.get_text())
        except logic.GiftError as exc:
            self._set_status(str(exc), True)
            return
        if not name:
            self._set_status(self.tr("noName"), True)
            return

        self.generate_button.set_sensitive(False)
        self.result.hide()
        self._set_status(self.tr("generating"))
        key = self.key_entry.get_text()
        manual = self.manual_entry.get_text()
        currency = self.currency

        def work() -> None:
            try:
                info = logic.resolve_rate(
                    date, evds_key=key, manual_rate=manual, currency=currency, lang=self.lang
                )
                GLib.idle_add(self._show_result, info, name, amount, iban)
            except logic.GiftError as exc:
                message = f"{exc} {self.tr('manualHint', currency=currency)}"
                GLib.idle_add(self._set_status, message, True)
            except Exception as exc:  # unexpected network/parsing failure
                GLib.idle_add(self._set_status, f"Beklenmeyen bir hata oluştu: {exc}", True)
            finally:
                GLib.idle_add(self.generate_button.set_sensitive, True)

        threading.Thread(target=work, daemon=True).start()

    def _show_result(self, info: logic.RateInfo, name: str, amount: float, iban: str) -> bool:
        self.last_result = (info, name, amount, iban)
        total = amount * info.rate
        source_key = {
            "TCMB EVDS": "sourceEvds",
            "ECB / Frankfurter": "sourcePublic",
            "Elle girilen kur": "sourceManual",
        }.get(info.source, "sourcePublic")
        source = self.tr(source_key)
        self.rate_label.set_text(f"{self.tr('rate')}: {info.rate:.4f} {self.currency}/TRY ({source}, {info.used_date})")
        self.total_label.set_text(f"{self.tr('total')}: {logic.format_amount(total, self.lang)} TL")
        self.message_view.get_buffer().set_text(logic.build_message(name, total, iban, self.lang))
        note_text = logic.note_text(info, self.lang)
        note = f" {note_text}" if note_text else ""
        self._set_status(self.tr("ready") + note)
        self.result.show()
        return False  # run once

    def _copy(self, _button: Gtk.Button) -> None:
        text = self.message_view.get_buffer().get_text()
        if not text:
            self._set_status(self.tr("noMessage"), True)
            return
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(text, -1)
        clipboard.store()
        self._set_status(self.tr("copied"))


def main() -> None:
    window = GiftApp()
    window.show_all()
    window.result.hide()  # show_all would otherwise reveal the empty result frame
    Gtk.main()


if __name__ == "__main__":
    main()
