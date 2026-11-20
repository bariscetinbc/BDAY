"""Exchange-rate lookup and message building for the birthday gift desktop app.

No web server is involved: this module only makes direct HTTPS requests when a
rate needs to be looked up. All public functions are usable without GTK, which
makes them easy to test.
"""

from __future__ import annotations

import datetime as dt
import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

EVDS_SERIES = "TP.DK.EUR.S.YTL"
EVDS_BASE = "https://evds3.tcmb.gov.tr/igmevdsms-dis/"
FRANKFURTER_BASE = "https://api.frankfurter.dev/v1/"
REQUEST_TIMEOUT = 15
USER_AGENT = "DogumGunuHediyesi/1.0"


class GiftError(Exception):
    """A problem the person can understand and fix in the app."""


@dataclass
class RateInfo:
    rate: float
    source: str
    used_date: str
    note: str = ""


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
        raise GiftError("Lütfen euro tutarını girin.")
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


def format_amount(value: float) -> str:
    """Turkish number formatting: 1234.5 -> 1.234,50"""
    return f"{value:,.2f}".replace(",", "\u0001").replace(".", ",").replace("\u0001", ".")


def build_message(name: str, amount_in_try: float, iban: str = "") -> str:
    """The exact wording requested by the person."""
    beginning = f"{name.strip()} iyiki doğdun. {format_amount(amount_in_try)} olarak doğum günü hediyemizi yolluyoruz."
    iban = iban.strip()
    return f"{beginning} {iban}" if iban else beginning


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


def fetch_evds_rate(date: dt.date, key: str) -> RateInfo:
    """TCMB EVDS EUR selling rate for the selected day, using the person's key."""
    if not key.strip():
        raise GiftError("EVDS için bir API anahtarı girin.")
    params = urllib.parse.urlencode(
        {
            "startDate": evds_date(date),
            "endDate": evds_date(date),
            "type": "json",
        }
    )
    url = f"{EVDS_BASE}series={EVDS_SERIES}&{params}"
    payload = _fetch_json(url, headers={"key": key.strip()})
    rate = _first_positive_value(payload)
    if rate is None:
        raise GiftError("EVDS bu tarih için bir kur döndürmedi.")
    return RateInfo(rate, "TCMB EVDS", iso_date(date))


def fetch_public_rate(date: dt.date) -> RateInfo:
    """Historical ECB EUR/TRY rate via the free Frankfurter service."""
    today = dt.date.today()
    if date > today:
        payload = _fetch_json(f"{FRANKFURTER_BASE}latest?base=EUR&symbols=TRY")
        note = "Seçtiğiniz tarih henüz gelmediği için en son kur kullanıldı."
    else:
        payload = _fetch_json(
            f"{FRANKFURTER_BASE}{iso_date(previous_business_day(date))}?base=EUR&symbols=TRY"
        )
        note = ""
    try:
        rate = float(payload["rates"]["TRY"])
        used_date = payload.get("date") or iso_date(date)
    except (KeyError, TypeError, ValueError) as exc:
        raise GiftError("Kur servisinden TRY değeri alınamadı.") from exc
    if rate <= 0:
        raise GiftError("Kur servisinden geçerli bir kur alınamadı.")
    if used_date != iso_date(date):
        note = f"Hafta sonu veya tatil nedeniyle {used_date} tarihinin kuru kullanıldı."
    return RateInfo(rate, "ECB / Frankfurter", used_date, note)


def resolve_rate(
    date: dt.date,
    evds_key: str = "",
    manual_rate: str = "",
    allow_network: bool = True,
) -> RateInfo:
    """Pick the rate source: typed rate > EVDS key > public service."""
    if manual_rate and manual_rate.strip():
        value = parse_amount(manual_rate)
        return RateInfo(value, "Elle girilen kur", iso_date(date), "Kur elle girildiği için internet kullanılmadı.")
    if not allow_network:
        raise GiftError("İnternet bağlantısı yok. Kur alanına TRY/EUR değerini elle yazabilirsiniz.")
    if evds_key and evds_key.strip():
        try:
            return fetch_evds_rate(date, evds_key)
        except GiftError as exc:
            # A wrong or expired key should not stop the person from working,
            # but they should be told why a different source was used.
            try:
                info = fetch_public_rate(date)
            except GiftError:
                raise exc
            prefix = f"EVDS kullanılamadı ({exc}); açık kur servisi kullanıldı."
            info.note = f"{prefix} {info.note}".strip()
            return info
    return fetch_public_rate(date)
