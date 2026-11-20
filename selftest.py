#!/usr/bin/env python3
"""Quick checks for the gift logic. Add --online to also test the live rate API."""

from __future__ import annotations

import datetime as dt
import sys

import gift_logic as logic

passed = 0


def check(label: str, condition: bool) -> None:
    global passed
    if not condition:
        raise AssertionError(label)
    passed += 1
    print(f"ok - {label}")


def main() -> None:
    check("date DD-MM-YYYY", logic.parse_date("01-05-2024") == dt.date(2024, 5, 1))
    check("date ISO", logic.parse_date("2024-05-01") == dt.date(2024, 5, 1))
    check("date dotted", logic.parse_date("01.05.2024") == dt.date(2024, 5, 1))
    check("EVDS date format", logic.evds_date(dt.date(2024, 5, 1)) == "01-05-2024")
    check("weekend fallback", logic.previous_business_day(dt.date(2024, 5, 4)) == dt.date(2024, 5, 3))

    check("amount comma", logic.parse_amount("25,50") == 25.5)
    check("amount dot", logic.parse_amount("1234.56") == 1234.56)
    check("amount Turkish thousands", logic.parse_amount("1.234,56") == 1234.56)
    check("amount plain", logic.parse_amount("25") == 25.0)

    check("Turkish formatting", logic.format_amount(1234.5) == "1.234,50")
    check(
        "exact message",
        logic.build_message("Elif", 867.6, "TR12 3456")
        == "Elif iyiki doğdun. 867,60 olarak doğum günü hediyemizi yolluyoruz. TR12 3456",
    )
    check(
        "message without IBAN",
        logic.build_message("Elif", 867.6, "") == "Elif iyiki doğdun. 867,60 olarak doğum günü hediyemizi yolluyoruz.",
    )

    sample = {"data": [{"values": [{"DATE": "01-05-2024", "VALUE": "34,7045"}]}]}
    check("EVDS payload parsing", logic._first_positive_value(sample) == 34.7045)

    manual = logic.resolve_rate(dt.date(2024, 5, 1), manual_rate="34,70", allow_network=False)
    check("manual rate needs no network", manual.rate == 34.7 and manual.source == "Elle girilen kur")

    if "--online" in sys.argv:
        info = logic.fetch_public_rate(dt.date(2024, 5, 1))
        check("live public rate", info.rate > 1 and info.used_date == "2024-04-30")
        print(f"     live rate: {info.rate} TRY/EUR on {info.used_date}")

    print(f"\n{passed} checks passed.")


if __name__ == "__main__":
    main()
