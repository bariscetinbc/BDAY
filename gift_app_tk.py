#!/usr/bin/env python3
"""Cross-platform desktop window for BDAY (Windows/macOS).

Uses Tk, which ships with the standard Python installers for Windows and macOS.
Currency, language and light/dark theme are selectable and remembered.
The Linux build keeps the GTK window in gift_app.py. Both use gift_logic.py.
"""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk

import gift_logic as logic


class GiftAppTk:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.messages: queue.Queue = queue.Queue()
        self.prefs = logic.load_preferences()
        self.lang = self.prefs["lang"]
        self.theme = self.prefs["theme"]
        self.currency = self.prefs["currency"]
        self.evds_key = self.prefs.get("evds_key", "")
        self.last_result = None
        self.muted_fg = "#666666"

        root.title("BDAY")
        root.geometry("660x760")
        root.minsize(580, 660)

        main = ttk.Frame(root, padding=18)
        main.grid(row=0, column=0, sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(11, weight=1)

        self.title = ttk.Label(main, font=("TkDefaultFont", 15, "bold"))
        self.title.grid(row=0, column=0, columnspan=3, sticky="w")

        self.subtitle = ttk.Label(main, wraplength=600, justify="left")
        self.subtitle.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 10))

        preferences = ttk.LabelFrame(main, padding=10)
        preferences.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        preferences.columnconfigure(1, weight=1)
        preferences.columnconfigure(3, weight=1)

        self.currency_label = ttk.Label(preferences)
        self.currency_label.grid(row=0, column=0, sticky="w")
        self.currency_combo = ttk.Combobox(preferences, state="readonly", width=10,
                                           values=list(logic.CURRENCIES))
        self.currency_combo.set(self.currency)
        self.currency_combo.grid(row=0, column=1, sticky="w", padx=(6, 16))
        self.currency_combo.bind("<<ComboboxSelected>>", self._currency_changed)

        self.language_label = ttk.Label(preferences)
        self.language_label.grid(row=0, column=2, sticky="w")
        self.language_combo = ttk.Combobox(preferences, state="readonly", width=10,
                                           values=["Türkçe", "English"])
        self.language_combo.set("Türkçe" if self.lang == "tr" else "English")
        self.language_combo.grid(row=0, column=3, sticky="w", padx=(6, 16))
        self.language_combo.bind("<<ComboboxSelected>>", self._language_changed)

        self.theme_button = ttk.Button(preferences, command=self._theme_toggled, width=14)
        self.theme_button.grid(row=0, column=4, sticky="w")

        self.date_label = ttk.Label(main, anchor="w")
        self.date_label.grid(row=3, column=0, sticky="w", pady=3)
        self.date = self._entry(main, 3)
        self.today_button = ttk.Button(main, command=self._today, width=9)
        self.today_button.grid(row=3, column=2, sticky="w", padx=(8, 0))

        self.name_label = ttk.Label(main, anchor="w")
        self.name_label.grid(row=4, column=0, sticky="w", pady=3)
        self.name = self._entry(main, 4)

        self.amount_label = ttk.Label(main, anchor="w")
        self.amount_label.grid(row=5, column=0, sticky="w", pady=3)
        self.amount = self._entry(main, 5)

        self.iban_label = ttk.Label(main, anchor="w")
        self.iban_label.grid(row=6, column=0, sticky="w", pady=3)
        self.iban = self._entry(main, 6)

        self.key_label = ttk.Label(main, anchor="w")
        self.key_label.grid(row=7, column=0, sticky="w", pady=3)
        self.key = self._entry(main, 7)
        self.forget_key_button = ttk.Button(main, command=self._forget_key, width=12)
        self.forget_key_button.grid(row=7, column=2, sticky="w", padx=(8, 0))

        self.manual_label = ttk.Label(main, anchor="w")
        self.manual_label.grid(row=8, column=0, sticky="w", pady=3)
        self.manual = self._entry(main, 8)

        actions = ttk.Frame(main)
        actions.grid(row=9, column=0, columnspan=3, sticky="w", pady=10)
        self.generate_button = ttk.Button(actions, command=self._generate)
        self.generate_button.grid(row=0, column=0)
        self.clear_button = ttk.Button(actions, command=self._clear)
        self.clear_button.grid(row=0, column=1, padx=(8, 0))

        self.status = ttk.Label(main, wraplength=600, justify="left")
        self.status.grid(row=10, column=0, columnspan=3, sticky="we")

        self.result = ttk.LabelFrame(main, padding=10)
        self.result.grid(row=11, column=0, columnspan=3, sticky="nsew", pady=(8, 0))
        self.result.columnconfigure(0, weight=1)

        self.rate_label = ttk.Label(self.result, anchor="w")
        self.rate_label.grid(row=0, column=0, sticky="w")
        self.total_label = ttk.Label(self.result, anchor="w")
        self.total_label.grid(row=1, column=0, sticky="w", pady=(2, 8))

        self.message = scrolledtext.ScrolledText(self.result, height=5, wrap="word")
        self.message.grid(row=2, column=0, sticky="nsew")
        self.message.configure(state="disabled")
        self.result.rowconfigure(2, weight=1)

        self.copy_button = ttk.Button(self.result, command=self._copy)
        self.copy_button.grid(row=3, column=0, sticky="w", pady=(8, 0))

        self.footnote = ttk.Label(main, wraplength=600, justify="left")
        self.footnote.grid(row=12, column=0, columnspan=3, sticky="w", pady=(10, 0))

        for entry in (self.date, self.name, self.amount, self.iban, self.key, self.manual):
            entry.bind("<Return>", lambda _event: self._generate())

        self._retranslate()
        if self.evds_key:
            self.key.delete(0, "end")
            self.key.insert(0, self.evds_key)
            self.key.configure(foreground=self._entry_fg())
        self.key.bind("<FocusOut>", lambda _event: self._remember_key())
        self._apply_theme()

    def tr(self, key: str, **variables) -> str:
        return logic.t(self.lang, key, **variables)

    def _entry(self, parent: ttk.Frame, row: int) -> ttk.Entry:
        entry = ttk.Entry(parent)
        entry.grid(row=row, column=1, sticky="ew", pady=3)
        return entry

    def _apply_theme(self) -> None:
        dark = self.theme == "dark"
        bg = "#202328" if dark else "#ffffff"
        fg = "#eef1f5" if dark else "#000000"
        field = "#191c20" if dark else "#ffffff"
        soft = "#262a30" if dark else "#f4f6f8"
        self.muted_fg = "#9aa4b0" if dark else "#666666"
        self.root.configure(background=bg)
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TLabelframe", background=bg, foreground=fg)
        style.configure("TLabelframe.Label", background=bg, foreground=fg)
        style.configure("TButton", background=soft, foreground=fg, borderwidth=1)
        style.map("TButton", background=[("active", field)])
        style.configure("TEntry", fieldbackground=field, foreground=fg, insertcolor=fg)
        style.configure("TCombobox", fieldbackground=field, foreground=fg,
                        background=soft, arrowcolor=fg)
        self.message.configure(background=field, foreground=fg, insertbackground=fg)

    def _save_preferences(self) -> None:
        logic.save_preferences(
            {
                "lang": self.lang,
                "theme": self.theme,
                "currency": self.currency,
                "evds_key": self.evds_key,
            }
        )

    def _update_forget_button(self) -> None:
        state = "normal" if self.evds_key else "disabled"
        self.forget_key_button.configure(state=state)

    def _remember_key(self) -> None:
        value = self._text(self.key, self.tr("keyPlaceholder")).strip()
        if value != self.evds_key:
            self.evds_key = value
            self._save_preferences()
        self._update_forget_button()

    def _forget_key(self) -> None:
        self.evds_key = ""
        self.key.delete(0, "end")
        self.key.configure(foreground=self._entry_fg())
        self._update_forget_button()
        self._save_preferences()
        self._set_status(self.tr("keyForgotten"))

    def _set_hints(self) -> None:
        hints = (
            (self.date, self.tr("datePlaceholder")),
            (self.name, self.tr("namePlaceholder")),
            (self.amount, self.tr("amountPlaceholder")),
            (self.iban, self.tr("ibanPlaceholder")),
            (self.key, self.tr("keyPlaceholder")),
            (self.manual, self.tr("manualPlaceholder")),
        )
        for entry, hint in hints:
            if not entry.get().strip() or entry.get() in [h[1] for h in hints]:
                entry.delete(0, "end")
                entry.insert(0, hint)
                entry.configure(foreground=self.muted_fg)
        self.key.configure(show="")

    def _retranslate(self) -> None:
        self.root.title("BDAY — " + self.tr("title"))
        self.title.configure(text=self.tr("title"))
        self.subtitle.configure(text=self.tr("subtitle"))
        self.result.configure(text=self.tr("result"))
        self.currency_label.configure(text=self.tr("currency"))
        self.language_label.configure(text=self.tr("language"))
        self.theme_button.configure(text=self.tr("themeDark") if self.theme == "light" else self.tr("themeLight"))
        self.date_label.configure(text=self.tr("date"))
        self.today_button.configure(text=self.tr("today"))
        self.name_label.configure(text=self.tr("name"))
        self.amount_label.configure(text=self.tr("amount") + " (" + self.currency + ")")
        self.iban_label.configure(text=self.tr("iban"))
        self.key_label.configure(text=self.tr("key"))
        self.manual_label.configure(text=self.tr("manual", currency=self.currency))
        self.generate_button.configure(text=self.tr("generate"))
        self.clear_button.configure(text=self.tr("clear"))
        self.copy_button.configure(text=self.tr("copy"))
        self.forget_key_button.configure(text=self.tr("forgetKey"))
        self.footnote.configure(text=self.tr("footnote"))
        self._set_hints()
        self._update_forget_button()

    def _currency_changed(self, _event=None) -> None:
        self.currency = self.currency_combo.get()
        self.last_result = None
        self._clear_result()
        self._retranslate()
        self._save_preferences()

    def _language_changed(self, _event=None) -> None:
        self.lang = "tr" if self.language_combo.get() == "Türkçe" else "en"
        self._retranslate()
        if self.last_result:
            info, name, amount, iban = self.last_result
            self._show_result(info, name, amount, iban)
        self._save_preferences()

    def _theme_toggled(self) -> None:
        self.theme = "dark" if self.theme == "light" else "light"
        self._apply_theme()
        self._retranslate()
        self._save_preferences()

    def _text(self, entry: ttk.Entry, placeholder: str) -> str:
        value = entry.get()
        return "" if value == placeholder else value.strip()

    def _set_status(self, text: str) -> None:
        self.status.configure(text=text)

    def _clear_result(self) -> None:
        self.message.configure(state="normal")
        self.message.delete("1.0", "end")
        self.message.configure(state="disabled")
        self.rate_label.configure(text="")
        self.total_label.configure(text="")

    def _today(self) -> None:
        import datetime as dt

        self.date.delete(0, "end")
        self.date.insert(0, dt.date.today().strftime("%d-%m-%Y"))
        self.date.configure(foreground=self._entry_fg())

    def _entry_fg(self) -> str:
        return "#eef1f5" if self.theme == "dark" else "#000000"

    def _clear(self) -> None:
        saved_key = self.evds_key
        self._set_hints()
        if saved_key:
            self.key.delete(0, "end")
            self.key.insert(0, saved_key)
            self.key.configure(foreground=self._entry_fg())
        self._clear_result()
        self._set_status("")

    def _generate(self) -> None:
        name = self._text(self.name, self.tr("namePlaceholder"))
        iban = self._text(self.iban, self.tr("ibanPlaceholder"))
        try:
            date = logic.parse_date(self._text(self.date, self.tr("datePlaceholder")))
            amount = logic.parse_amount(self._text(self.amount, self.tr("amountPlaceholder")))
        except logic.GiftError as exc:
            self._set_status(str(exc))
            return
        if not name:
            self._set_status(self.tr("noName"))
            return

        self._remember_key()
        key = self.evds_key
        manual = self._text(self.manual, self.tr("manualPlaceholder"))
        currency = self.currency
        self.generate_button.configure(state="disabled")
        self._set_status(self.tr("generating"))

        def work() -> None:
            try:
                info = logic.resolve_rate(
                    date, evds_key=key, manual_rate=manual, currency=currency, lang=self.lang
                )
            except logic.GiftError as exc:
                self.messages.put(("error", f"{exc} {self.tr('manualHint', currency=currency)}"))
            except Exception as exc:  # unexpected failure: keep the app usable
                self.messages.put(("error", f"Beklenmeyen bir hata oluştu: {exc}"))
            else:
                self.messages.put(("ok", info, name, amount, iban))

        threading.Thread(target=work, daemon=True).start()
        self.root.after(100, self._drain)

    def _drain(self) -> None:
        try:
            item = self.messages.get_nowait()
        except queue.Empty:
            self.root.after(100, self._drain)
            return
        if item[0] == "error":
            self._set_status(item[1])
        else:
            _kind, info, name, amount, iban = item
            self._show_result(info, name, amount, iban)
        self.generate_button.configure(state="normal")

    def _show_result(self, info: logic.RateInfo, name: str, amount: float, iban: str) -> None:
        self.last_result = (info, name, amount, iban)
        total = amount * info.rate
        source_key = {
            "TCMB EVDS": "sourceEvds",
            "ECB / Frankfurter": "sourcePublic",
            "Elle girilen kur": "sourceManual",
        }.get(info.source, "sourcePublic")
        self.rate_label.configure(
            text=f"{self.tr('rate')}: {info.rate:.4f} {self.currency}/TRY ({self.tr(source_key)}, {info.used_date})"
        )
        self.total_label.configure(text=f"{self.tr('total')}: {logic.format_amount(total, self.lang)} TL")
        self.message.configure(state="normal")
        self.message.delete("1.0", "end")
        self.message.insert("1.0", logic.build_message(name, total, iban, self.lang))
        self.message.configure(state="disabled")
        note_text = logic.note_text(info, self.lang)
        note = f" {note_text}" if note_text else ""
        self._set_status(self.tr("ready") + note)

    def _copy(self) -> None:
        self.message.configure(state="normal")
        text = self.message.get("1.0", "end").strip()
        self.message.configure(state="disabled")
        if not text:
            self._set_status(self.tr("noMessage"))
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self._set_status(self.tr("copied"))


def main() -> None:
    root = tk.Tk()
    GiftAppTk(root)
    root.mainloop()


if __name__ == "__main__":
    main()
