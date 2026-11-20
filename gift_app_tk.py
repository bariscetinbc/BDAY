#!/usr/bin/env python3
"""Cross-platform desktop window for the birthday gift tool (Windows/macOS).

Uses Tk, which ships with the standard Python installers for Windows and macOS.
The Linux build keeps the existing GTK window in gift_app.py. Both windows use
the exact same calculation code in gift_logic.py.
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

        root.title("Doğum Günü Hediyesi")
        root.geometry("640x700")
        root.minsize(560, 600)

        main = ttk.Frame(root, padding=18)
        main.grid(row=0, column=0, sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(9, weight=1)

        title = ttk.Label(main, text="Doğum günü hediye mesajı", font=("TkDefaultFont", 15, "bold"))
        title.grid(row=0, column=0, columnspan=3, sticky="w")

        subtitle = ttk.Label(
            main,
            text="Tarih, ad, euro tutarı ve IBAN ile mesajı hazırla. Kur, TCMB EVDS veya açık kur verisinden alınır.",
            wraplength=580,
            justify="left",
        )
        subtitle.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 12))

        self.date = self._field(main, 2, "Tarih (GG-AA-YYYY)", "Örn. 01-05-2024")
        ttk.Button(main, text="Bugün", command=self._today, width=9).grid(row=2, column=2, sticky="w", padx=(8, 0))
        self.name = self._field(main, 3, "Ad", "Örn. Elif")
        self.amount = self._field(main, 4, "Tutar (EUR)", "Örn. 25,50")
        self.iban = self._field(main, 5, "IBAN (isteğe bağlı)", "TR00 0000 0000 0000 0000 0000 00")
        self.key = self._field(main, 6, "EVDS anahtarı (isteğe bağlı)", "Anahtarınız varsa girin")
        self.key.configure(show="•")
        self.manual = self._field(main, 7, "Kur elle (isteğe bağlı)", "Örn. 34,70 — internet yoksa")

        actions = ttk.Frame(main)
        actions.grid(row=8, column=0, columnspan=3, sticky="w", pady=12)
        self.generate_button = ttk.Button(actions, text="Kuru al ve mesajı oluştur", command=self._generate)
        self.generate_button.grid(row=0, column=0)
        ttk.Button(actions, text="Alanları temizle", command=self._clear).grid(row=0, column=1, padx=(8, 0))

        self.status = ttk.Label(main, text="", foreground="#8a1c1c", wraplength=580, justify="left")
        self.status.grid(row=9, column=0, columnspan=3, sticky="we")

        result = ttk.LabelFrame(main, text="Hazır mesaj", padding=10)
        result.grid(row=10, column=0, columnspan=3, sticky="nsew", pady=(8, 0))
        result.columnconfigure(0, weight=1)

        self.rate_label = ttk.Label(result, text="Kur: –", anchor="w")
        self.rate_label.grid(row=0, column=0, sticky="w")
        self.total_label = ttk.Label(result, text="TL tutarı: –", anchor="w")
        self.total_label.grid(row=1, column=0, sticky="w", pady=(2, 8))

        self.message = scrolledtext.ScrolledText(result, height=5, wrap="word")
        self.message.grid(row=2, column=0, sticky="nsew")
        self.message.configure(state="disabled")
        result.rowconfigure(2, weight=1)

        copy = ttk.Button(result, text="Mesajı kopyala", command=self._copy)
        copy.grid(row=3, column=0, sticky="w", pady=(8, 0))

        footnote = ttk.Label(
            main,
            text="Kur kaynağı: TCMB EVDS (anahtar girilirse), aksi halde ECB / Frankfurter. İnternet yoksa kur elle girilebilir.",
            wraplength=580,
            justify="left",
            foreground="#555555",
        )
        footnote.grid(row=11, column=0, columnspan=3, sticky="w", pady=(10, 0))

        for entry in (self.date, self.name, self.amount, self.iban, self.key, self.manual):
            entry.bind("<Return>", lambda _event: self._generate())

    @staticmethod
    def _field(parent: ttk.Frame, row: int, label: str, placeholder: str) -> ttk.Entry:
        ttk.Label(parent, text=label, anchor="w").grid(row=row, column=0, sticky="w", pady=3)
        entry = ttk.Entry(parent)
        entry.insert(0, "")
        entry.grid(row=row, column=1, sticky="ew", pady=3)
        # Placeholder as a one-time hint; the value itself stays empty.
        entry.configure(foreground="#666666")
        entry.insert(0, placeholder)
        entry.bind("<FocusIn>", lambda _e, e=entry, p=placeholder: GiftAppTk._clear_placeholder(e, p))
        entry.bind("<FocusOut>", lambda _e, e=entry, p=placeholder: GiftAppTk._restore_placeholder(e, p))
        return entry

    @staticmethod
    def _clear_placeholder(entry: ttk.Entry, placeholder: str) -> None:
        if entry.get() == placeholder:
            entry.delete(0, "end")
            entry.configure(foreground="#000000")
            if placeholder == "Anahtarınız varsa girin":
                entry.configure(show="•")

    @staticmethod
    def _restore_placeholder(entry: ttk.Entry, placeholder: str) -> None:
        if not entry.get().strip():
            entry.insert(0, placeholder)
            entry.configure(foreground="#666666")
            entry.configure(show="" if placeholder == "Anahtarınız varsa girin" else entry.cget("show"))

    def _text(self, entry: ttk.Entry, placeholder: str = "") -> str:
        value = entry.get()
        return "" if value == placeholder else value.strip()

    def _set_status(self, text: str) -> None:
        self.status.configure(text=text)

    def _today(self) -> None:
        import datetime as dt

        self._clear_placeholder(self.date, "Örn. 01-05-2024")
        self.date.delete(0, "end")
        self.date.insert(0, dt.date.today().strftime("%d-%m-%Y"))
        self.date.configure(foreground="#000000")

    def _clear(self) -> None:
        for entry, placeholder in (
            (self.date, "Örn. 01-05-2024"),
            (self.name, "Örn. Elif"),
            (self.amount, "Örn. 25,50"),
            (self.iban, "TR00 0000 0000 0000 0000 0000 00"),
            (self.key, "Anahtarınız varsa girin"),
            (self.manual, "Örn. 34,70 — internet yoksa"),
        ):
            entry.delete(0, "end")
            entry.insert(0, placeholder)
            entry.configure(foreground="#666666")
        self.key.configure(show="")
        self.message.configure(state="normal")
        self.message.delete("1.0", "end")
        self.message.configure(state="disabled")
        self.rate_label.configure(text="Kur: –")
        self.total_label.configure(text="TL tutarı: –")
        self._set_status("")

    def _generate(self) -> None:
        name = self._text(self.name, "Örn. Elif")
        iban = self._text(self.iban, "TR00 0000 0000 0000 0000 0000 00")
        try:
            date = logic.parse_date(self._text(self.date, "Örn. 01-05-2024"))
            amount_eur = logic.parse_amount(self._text(self.amount, "Örn. 25,50"))
        except logic.GiftError as exc:
            self._set_status(str(exc))
            return
        if not name:
            self._set_status("Lütfen adı girin.")
            return

        key = self._text(self.key, "Anahtarınız varsa girin")
        manual = self._text(self.manual, "Örn. 34,70 — internet yoksa")
        self.generate_button.configure(state="disabled")
        self._set_status("Kur alınıyor…")

        def work() -> None:
            try:
                info = logic.resolve_rate(date, evds_key=key, manual_rate=manual)
            except logic.GiftError as exc:
                self.messages.put(("error", f"{exc} Kur alanına TRY/EUR değerini elle yazabilirsiniz."))
            except Exception as exc:  # unexpected failure: keep the app usable
                self.messages.put(("error", f"Beklenmeyen bir hata oluştu: {exc}"))
            else:
                self.messages.put(("ok", name, amount_eur, iban, info))

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
            _kind, name, amount_eur, iban, info = item
            total = amount_eur * info.rate
            message = logic.build_message(name, total, iban)
            self.rate_label.configure(
                text=f"Kur: {info.rate:.4f} TRY/EUR ({info.source}, {info.used_date})"
            )
            self.total_label.configure(text=f"TL tutarı: {logic.format_amount(total)} TL")
            self.message.configure(state="normal")
            self.message.delete("1.0", "end")
            self.message.insert("1.0", message)
            self.message.configure(state="disabled")
            note = f" {info.note}" if info.note else ""
            self._set_status("Mesaj hazır." + note)
        self.generate_button.configure(state="normal")

    def _copy(self) -> None:
        self.message.configure(state="normal")
        text = self.message.get("1.0", "end").strip()
        self.message.configure(state="disabled")
        if not text:
            self._set_status("Önce mesajı oluşturun.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self._set_status("Mesaj kopyalandı.")


def main() -> None:
    root = tk.Tk()
    GiftAppTk(root)
    root.mainloop()


if __name__ == "__main__":
    main()
