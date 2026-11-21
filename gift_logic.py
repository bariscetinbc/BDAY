"""Exchange-rate lookup, translations and message building for BDAY.

No web server is involved: this module only makes direct HTTPS requests when a
rate needs to be looked up. All public functions are usable without GTK/Tk,
which makes them easy to test.
"""

from __future__ import annotations

import datetime as dt
import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

EVDS_BASE = "https://evds3.tcmb.gov.tr/igmevdsms-dis/"
FRANKFURTER_BASE = "https://api.frankfurter.dev/v1/"
REQUEST_TIMEOUT = 15
USER_AGENT = "BDAY/5.0"

# Currency -> TCMB EVDS selling-rate series. EUR is the series documented in the
# EVDS manual; the others follow the same published TP.DK.<CUR>.S.YTL pattern.
CURRENCIES = {
    "EUR": {"evds": "TP.DK.EUR.S.YTL", "tr": "Euro", "en": "Euro"},
    "USD": {"evds": "TP.DK.USD.S.YTL", "tr": "ABD doları", "en": "US dollar"},
    "GBP": {"evds": "TP.DK.GBP.S.YTL", "tr": "İngiliz sterlini", "en": "British pound"},
    "CHF": {"evds": "TP.DK.CHF.S.YTL", "tr": "İsviçre frangı", "en": "Swiss franc"},
}

PREFERENCES_FILE = Path.home() / ".bday.json"
LEGACY_PREFERENCES_FILE = Path.home() / ".dogum-gunu-hediyesi.json"

STRINGS = {
    "tr": {
        "title": "Doğum günü hediye mesajı",
        "subtitle": "Tarih, ad, para birimi ve tutar ile mesajı hazırla. Kur TCMB EVDS veya açık kur verisinden alınır.",
        "date": "Tarih (GG-AA-YYYY)",
        "datePlaceholder": "Örn. 01-05-2024",
        "calendar": "Takvim",
        "today": "Bugün",
        "name": "Ad",
        "namePlaceholder": "Örn. Elif",
        "amount": "Tutar",
        "amountPlaceholder": "Örn. 25,50",
        "iban": "IBAN",
        "ibanPlaceholder": "TR00 0000 0000 0000 0000 0000 00",
        "currency": "Para birimi",
        "language": "Dil",
        "theme": "Tema",
        "themeLight": "Açık tema",
        "themeDark": "Koyu tema",
        "key": "EVDS anahtarı (isteğe bağlı)",
        "keyPlaceholder": "Anahtarınız varsa girin",
        "keyRestored": "Kayıtlı anahtar geri yüklendi. Unutana kadar saklanır.",
        "forgetKey": "Anahtarı unut",
        "keyForgotten": "Kayıtlı anahtar silindi.",
        "manual": "Kur elle ({currency} / TRY, isteğe bağlı)",
        "manualPlaceholder": "Örn. 34,70 — internet yoksa",
        "generate": "Kuru al ve mesajı oluştur",
        "generating": "Kur alınıyor…",
        "clear": "Alanları temizle",
        "result": "Hazır mesaj",
        "rate": "Kur",
        "total": "TL tutarı",
        "copy": "Mesajı kopyala",
        "footnote": "Kur kaynağı: TCMB EVDS (anahtar girilirse), aksi halde ECB / Frankfurter. İnternet yoksa kur elle girilebilir.",
        "msg": "{name} iyiki doğdun. {amount} olarak doğum günü hediyemizi yolluyoruz.",
        "ready": "Mesaj hazır.",
        "noName": "Lütfen adı girin.",
        "noMessage": "Önce mesajı oluşturun.",
        "copied": "Mesaj kopyalandı.",
        "manualHint": "Kur alanına TRY/{currency} değerini elle yazabilirsiniz.",
        "rateDate": "Kur tarihi",
        "sourceEvds": "TCMB EVDS",
        "sourcePublic": "ECB / Frankfurter",
        "sourceManual": "Elle girilen kur",
        "noteManual": "Kur elle girildiği için internet kullanılmadı.",
        "noteFuture": "Seçtiğiniz tarih henüz gelmediği için en son kur kullanıldı.",
        "noteWeekend": "Hafta sonu veya tatil nedeniyle {date} tarihinin kuru kullanıldı.",
        "noteEvdsFail": "TCMB EVDS kullanılamadı ({reason}); açık kur servisi kullanıldı.",
        "selectDate": "Tarih seç",
        "select": "Seç",
    },
    "en": {
        "title": "Birthday gift message",
        "subtitle": "Enter a date, name, currency and amount to prepare the message. The rate comes from TCMB EVDS or public rate data.",
        "date": "Date (DD-MM-YYYY)",
        "datePlaceholder": "e.g. 01-05-2024",
        "calendar": "Calendar",
        "today": "Today",
        "name": "Name",
        "namePlaceholder": "e.g. Elif",
        "amount": "Amount",
        "amountPlaceholder": "e.g. 25.50",
        "iban": "IBAN",
        "ibanPlaceholder": "TR00 0000 0000 0000 0000 0000 00",
        "currency": "Currency",
        "language": "Language",
        "theme": "Theme",
        "themeLight": "Light theme",
        "themeDark": "Dark theme",
        "key": "EVDS key (optional)",
        "keyPlaceholder": "Enter your key if you have one",
        "keyRestored": "Saved key restored. It stays saved until you forget it.",
        "forgetKey": "Forget key",
        "keyForgotten": "Saved key removed.",
        "manual": "Rate manually ({currency} / TRY, optional)",
        "manualPlaceholder": "e.g. 34.70 — when offline",
        "generate": "Get the rate and create the message",
        "generating": "Getting the rate…",
        "clear": "Clear fields",
        "result": "Ready message",
        "rate": "Rate",
        "total": "TRY amount",
        "copy": "Copy message",
        "footnote": "Rate source: TCMB EVDS (if a key is entered), otherwise ECB / Frankfurter. Offline? Enter the rate manually.",
        "msg": "Happy birthday, {name}! We are sending your birthday gift of {amount}.",
        "ready": "Message ready.",
        "noName": "Please enter the name.",
        "noMessage": "Please create the message first.",
        "copied": "Message copied.",
        "manualHint": "You can type the TRY/{currency} rate manually.",
        "rateDate": "Rate date",
        "sourceEvds": "TCMB EVDS",
        "sourcePublic": "ECB / Frankfurter",
        "sourceManual": "Entered manually",
        "noteManual": "No internet was used because the rate was entered manually.",
        "noteFuture": "The selected date is in the future, so the latest rate was used.",
        "noteWeekend": "Because of a weekend or holiday, the rate for {date} was used.",
        "noteEvdsFail": "TCMB EVDS was unavailable ({reason}); public rate data was used.",
        "selectDate": "Choose a date",
        "select": "Select",
    },
}


def t(lang: str, key: str, **variables) -> str:
    """Translate a UI string, falling back to Turkish."""
    table = STRINGS.get(lang, STRINGS["tr"])
    text = table.get(key, STRINGS["tr"].get(key, key))
    for name, value in variables.items():
        text = text.replace("{" + name + "}", str(value))
    return text


def load_preferences() -> dict:
    """Read saved language, theme, currency and EVDS key choices."""
    defaults = {"lang": "tr", "theme": "light", "currency": "EUR", "evds_key": ""}
    try:
        source = PREFERENCES_FILE if PREFERENCES_FILE.exists() else LEGACY_PREFERENCES_FILE
        data = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return defaults
    except (OSError, ValueError):
        return defaults
    if data.get("lang") in STRINGS:
        defaults["lang"] = data["lang"]
    if data.get("theme") in ("light", "dark"):
        defaults["theme"] = data["theme"]
    if data.get("currency") in CURRENCIES:
        defaults["currency"] = data["currency"]
    if isinstance(data.get("evds_key"), str):
        defaults["evds_key"] = data["evds_key"]
    return defaults


def save_preferences(preferences: dict) -> None:
    """Remember language, theme, currency and key between runs (best effort)."""
    try:
        PREFERENCES_FILE.write_text(
            json.dumps(preferences, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        # The key is a personal credential: keep the file private where possible.
        PREFERENCES_FILE.chmod(0o600)
    except OSError:
        pass


class GiftError(Exception):
    """A problem the person can understand and fix in the app."""


@dataclass
class RateInfo:
    rate: float
    source: str
    used_date: str
    note: str = ""
    note_key: str = ""
    note_vars: dict | None = None


def parse_date(text: str) -> dt.date:
    """Accept the date formats people commonly type into the field."""
    value = (text or "").strip()
    if not value:
        raise GiftError("Lütfen bir tarih girin.")
    for fmt in ("%d-%m-%Y", "%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise GiftError("Tarihi GG-AA-YYYY biçiminde yazın (örn. 01-05-2024).")


def evds_date(date: dt.date) -> str:
    """EVDS expects DD-MM-YYYY."""
    return date.strftime("%d-%m-%Y")


def iso_date(date: dt.date) -> str:
    return date.isoformat()


def previous_business_day(date: dt.date) -> dt.date:
    day = date
    while day.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        day -= dt.timedelta(days=1)
    return day


def parse_amount(text: str) -> float:
    """Read amounts such as 25, 25.5, 1.234,56 or 1234,56."""
    value = (text or "").strip().replace(" ", "").replace("EUR", "").replace("€", "")
    if not value:
        raise GiftError("Lütfen tutarı girin.")
    if "," in value and "." in value:
        if value.rfind(",") > value.rfind("."):
            value = value.replace(".", "").replace(",", ".")
        else:
            value = value.replace(",", "")
    elif "," in value:
        value = value.replace(",", ".")
    try:
        amount = float(value)
    except ValueError as exc:
        raise GiftError("Tutarı sayı olarak yazın (örn. 25 veya 25,50).") from exc
    if amount <= 0:
        raise GiftError("Tutar sıfırdan büyük olmalı.")
    return amount


def format_amount(value: float, lang: str = "tr") -> str:
    """Number formatting for the chosen language."""
    if lang == "en":
        return f"{value:,.2f}"
    return f"{value:,.2f}".replace(",", "\u0001").replace(".", ",").replace("\u0001", ".")


def build_message(name: str, amount_in_try: float, iban: str = "", lang: str = "tr") -> str:
    """The exact Turkish wording the person requested, or an English version."""
    beginning = t(
        lang, "msg", name=name.strip(), amount=format_amount(amount_in_try, lang)
    )
    iban = iban.strip()
    return f"{beginning} {iban}" if iban else beginning


def note_text(info: "RateInfo", lang: str = "tr") -> str:
    """Render a rate note in the current interface language when possible."""
    if info.note_key:
        return t(lang, info.note_key, **(info.note_vars or {}))
    return info.note


def _fetch_json(url: str, headers: dict | None = None) -> dict:
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json", **(headers or {})}
    )
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as exc:
        raise GiftError(f"Kur servisi HTTP {exc.code} yanıtı verdi.") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise GiftError("Kur servisine ulaşılamadı.") from exc
    except (ValueError, json.JSONDecodeError) as exc:
        raise GiftError("Kur servisinden okunamayan bir yanıt geldi.") from exc


def _first_positive_value(payload) -> float | None:
    """EVDS versions differ in how they wrap the observation value."""
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        items = payload.get("data") or payload.get("Items") or payload.get("items") or []
    else:
        items = []
    for item in items:
        if not isinstance(item, dict):
            continue
        values = item.get("values") or item.get("Values") or item.get("Data") or item.get("data") or []
        if isinstance(values, dict):
            values = list(values.values())
        for entry in values:
            if isinstance(entry, dict):
                raw = entry.get("VALUE", entry.get("Value", entry.get("value")))
            else:
                raw = entry
            try:
                number = float(str(raw).replace(",", "."))
            except (TypeError, ValueError):
                continue
            if number > 0:
                return number
    return None


def evds_series(currency: str) -> str:
    return CURRENCIES.get(currency, CURRENCIES["EUR"])["evds"]


def currency_label(currency: str, lang: str = "tr") -> str:
    return CURRENCIES.get(currency, CURRENCIES["EUR"]).get(lang, currency)


def fetch_evds_rate(date: dt.date, key: str, currency: str = "EUR") -> RateInfo:
    """TCMB EVDS selling rate for the selected day and currency."""
    if not key.strip():
        raise GiftError("EVDS için bir API anahtarı girin.")
    params = urllib.parse.urlencode(
        {
            "startDate": evds_date(date),
            "endDate": evds_date(date),
            "type": "json",
        }
    )
    url = f"{EVDS_BASE}series={evds_series(currency)}&{params}"
    payload = _fetch_json(url, headers={"key": key.strip()})
    rate = _first_positive_value(payload)
    if rate is None:
        raise GiftError("EVDS bu tarih için bir kur döndürmedi.")
    return RateInfo(rate, "TCMB EVDS", iso_date(date))


def fetch_public_rate(
    date: dt.date, currency: str = "EUR", lang: str = "tr"
) -> RateInfo:
    """Historical ECB rate for the chosen currency via the free Frankfurter service."""
    today = dt.date.today()
    note_key = ""
    note_vars: dict = {}
    if date > today:
        payload = _fetch_json(f"{FRANKFURTER_BASE}latest?base={currency}&symbols=TRY")
        note_key = "noteFuture"
    else:
        payload = _fetch_json(
            f"{FRANKFURTER_BASE}{iso_date(previous_business_day(date))}?base={currency}&symbols=TRY"
        )
    try:
        rate = float(payload["rates"]["TRY"])
        used_date = payload.get("date") or iso_date(date)
    except (KeyError, TypeError, ValueError) as exc:
        raise GiftError("Kur servisinden TRY değeri alınamadı.") from exc
    if rate <= 0:
        raise GiftError("Kur servisinden geçerli bir kur alınamadı.")
    if used_date != iso_date(date):
        note_key = "noteWeekend"
        note_vars = {"date": used_date}
    note = t(lang, note_key, **note_vars) if note_key else ""
    return RateInfo(rate, "ECB / Frankfurter", used_date, note, note_key, note_vars)


def resolve_rate(
    date: dt.date,
    evds_key: str = "",
    manual_rate: str = "",
    allow_network: bool = True,
    currency: str = "EUR",
    lang: str = "tr",
) -> RateInfo:
    """Pick the rate source: typed rate > EVDS key > public service."""
    if manual_rate and manual_rate.strip():
        value = parse_amount(manual_rate)
        return RateInfo(
            value, "Elle girilen kur", iso_date(date), t(lang, "noteManual"), "noteManual"
        )
    if not allow_network:
        raise GiftError(f"İnternet bağlantısı yok. Kur alanına TRY/{currency} değerini elle yazabilirsiniz.")
    if evds_key and evds_key.strip():
        try:
            return fetch_evds_rate(date, evds_key, currency)
        except GiftError as exc:
            # A wrong or expired key should not stop the person from working,
            # but they should be told why a different source was used.
            try:
                info = fetch_public_rate(date, currency, lang)
            except GiftError:
                raise exc
            prefix = t(lang, "noteEvdsFail", reason=exc)
            info.note = f"{prefix} {note_text(info, lang)}".strip()
            info.note_key = ""
            info.note_vars = None
            return info
    return fetch_public_rate(date, currency, lang)
