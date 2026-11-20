/* Doğum Günü Hediyesi — date, EUR amount and IBAN in; Turkish gift message out. */
(function () {
  "use strict";

  var EVDS_SERIES = "TP.DK.EUR.S.YTL";
  var EVDS_BASE = "https://evds3.tcmb.gov.tr/igmevdsms-dis/";
  var FRANKFURTER_BASE = "https://api.frankfurter.dev/v1/";

  var form = document.getElementById("giftForm");
  var fields = {
    date: document.getElementById("date"),
    name: document.getElementById("name"),
    amount: document.getElementById("amount"),
    iban: document.getElementById("iban"),
    key: document.getElementById("evdsKey"),
    manual: document.getElementById("manualRate")
  };
  var generateButton = document.getElementById("generate");
  var clearButton = document.getElementById("clear");
  var statusLine = document.getElementById("status");
  var result = document.getElementById("result");
  var rateValue = document.getElementById("rateValue");
  var rateSource = document.getElementById("rateSource");
  var convertedValue = document.getElementById("convertedValue");
  var usedDate = document.getElementById("usedDate");
  var rateNote = document.getElementById("rateNote");
  var message = document.getElementById("message");
  var copyButton = document.getElementById("copy");
  var copyFeedback = document.getElementById("copyFeedback");

  function fail(text) { throw new Error(text); }

  function pad(value) { return String(value).padStart(2, "0"); }

  function toEvdsDate(date) {
    return pad(date.getUTCDate()) + "-" + pad(date.getUTCMonth() + 1) + "-" + date.getUTCFullYear();
  }

  function toIsoDate(date) {
    return date.getUTCFullYear() + "-" + pad(date.getUTCMonth() + 1) + "-" + pad(date.getUTCDate());
  }

  function toLongDate(iso) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(iso || "")) return iso || "–";
    var parts = iso.split("-");
    return parts[2] + "." + parts[1] + "." + parts[0];
  }

  function parseDate(text) {
    var value = (text || "").trim().replace(/\s+/g, "");
    if (!value) fail("Lütfen bir tarih girin.");
    var match = value.match(/^(\d{1,4})[-/.](\d{1,2})[-/.](\d{1,4})$/);
    if (!match) fail("Tarihi GG-AA-YYYY biçiminde yazın (örn. 01-05-2024).");
    var a = Number(match[1]);
    var b = Number(match[2]);
    var c = Number(match[3]);
    var year, month, day;
    if (match[1].length === 4) {
      year = a; month = b; day = c;
    } else {
      year = c; day = a; month = b;
    }
    if (year < 1900 || year > 2200 || month < 1 || month > 12 || day < 1 || day > 31) {
      fail("Tarih geçerli değil. GG-AA-YYYY biçimini kullanın.");
    }
    var date = new Date(Date.UTC(year, month - 1, day));
    if (date.getUTCFullYear() !== year || date.getUTCMonth() !== month - 1 || date.getUTCDate() !== day) {
      fail("Bu tarih takvimde yok (örn. 31-02-2024).");
    }
    return date;
  }

  function previousBusinessDay(date) {
    var day = new Date(date.getTime());
    while (day.getUTCDay() === 0 || day.getUTCDay() === 6) {
      day.setUTCDate(day.getUTCDate() - 1);
    }
    return day;
  }

  function parseAmount(text) {
    var value = (text || "").trim().replace(/\s/g, "").replace(/EUR/gi, "").replace("€", "");
    if (!value) fail("Lütfen euro tutarını girin.");
    if (value.indexOf(",") !== -1 && value.indexOf(".") !== -1) {
      if (value.lastIndexOf(",") > value.lastIndexOf(".")) {
        value = value.replace(/\./g, "").replace(",", ".");
      } else {
        value = value.replace(/,/g, "");
      }
    } else if (value.indexOf(",") !== -1) {
      value = value.replace(/,/g, ".");
    }
    if (!/^\d+(\.\d+)?$/.test(value)) fail("Tutarı sayı olarak yazın (örn. 25 veya 25,50).");
    var amount = Number(value);
    if (!isFinite(amount) || amount <= 0) fail("Tutar sıfırdan büyük olmalı.");
    return amount;
  }

  function groupInteger(text) { return text.replace(/\B(?=(\d{3})+(?!\d))/g, "."); }

  function formatMoney(value) {
    var fixed = Math.round(value * 100) / 100;
    var parts = fixed.toFixed(2).split(".");
    return groupInteger(parts[0]) + "," + parts[1];
  }

  function formatRate(value) {
    var text = value.toFixed(4).replace(/0+$/, "").replace(/\.$/, "");
    var parts = text.split(".");
    return groupInteger(parts[0]) + (parts[1] ? "," + parts[1] : "");
  }

  function buildMessage(name, amountInTry, iban) {
    var beginning = name.trim() + " iyiki doğdun. " + formatMoney(amountInTry) +
      " olarak doğum günü hediyemizi yolluyoruz.";
    var cleanIban = (iban || "").trim();
    return cleanIban ? beginning + " " + cleanIban : beginning;
  }

  function fetchJson(url, options, timeoutMs) {
    var controller = new AbortController();
    var timer = setTimeout(function () { controller.abort(); }, timeoutMs || 9000);
    var settings = Object.assign({ signal: controller.signal, cache: "no-store" }, options || {});
    return fetch(url, settings).then(function (response) {
      if (!response.ok) fail("Kur servisi HTTP " + response.status + " yanıtı verdi.");
      return response.json();
    }).catch(function (error) {
      if (error && error.name === "AbortError") fail("Kur servisi zaman aşımına uğradı.");
      if (error && typeof error.message === "string" && /^Kur |^TCMB |^EVDS |^Seçtiğiniz/.test(error.message)) {
        throw error;
      }
      fail("Kur servisine ulaşılamadı. Kur alanına elle yazabilirsiniz.");
    }).finally(function () { clearTimeout(timer); });
  }

  function firstPositiveValue(payload) {
    var items = Array.isArray(payload) ? payload :
      (payload && (payload.data || payload.Items || payload.items)) || [];
    if (!Array.isArray(items)) return null;
    for (var i = 0; i < items.length; i += 1) {
      var item = items[i];
      if (!item || typeof item !== "object") continue;
      var values = item.values || item.Values || item.Data || item.data || [];
      if (values && !Array.isArray(values) && typeof values === "object") values = Object.values(values);
      if (!Array.isArray(values)) continue;
      for (var j = 0; j < values.length; j += 1) {
        var entry = values[j];
        var raw = entry && typeof entry === "object" ? (entry.VALUE || entry.Value || entry.value) : entry;
        var number = Number(String(raw == null ? "" : raw).replace(",", "."));
        if (isFinite(number) && number > 0) return number;
      }
    }
    return null;
  }

  function fetchEvdsRate(date, key) {
    var query = "series=" + EVDS_SERIES +
      "&startDate=" + encodeURIComponent(toEvdsDate(date)) +
      "&endDate=" + encodeURIComponent(toEvdsDate(date)) +
      "&type=json";
    return fetchJson(EVDS_BASE + query, { headers: { key: key, Accept: "application/json" } }, 8000)
      .then(function (payload) {
        var rate = firstPositiveValue(payload);
        if (rate === null) fail("EVDS bu tarih için kur döndürmedi.");
        return { rate: rate, source: "TCMB EVDS", usedDate: toIsoDate(date), note: "" };
      });
  }

  function fetchPublicRate(date) {
    var today = new Date();
    var isFuture = toIsoDate(date) > toIsoDate(new Date(Date.UTC(today.getFullYear(), today.getMonth(), today.getDate())));
    var wantedDate = isFuture ? null : previousBusinessDay(date);
    var url = isFuture
      ? FRANKFURTER_BASE + "latest?base=EUR&symbols=TRY"
      : FRANKFURTER_BASE + toIsoDate(wantedDate) + "?base=EUR&symbols=TRY";
    return fetchJson(url, null, 10000).then(function (payload) {
      var rate = payload && payload.rates ? Number(payload.rates.TRY) : NaN;
      if (!isFinite(rate) || rate <= 0) fail("Kur servisinden geçerli bir TRY değeri alınamadı.");
      var usedDate = (payload && payload.date) || toIsoDate(date);
      var note = "";
      if (isFuture) {
        note = "Seçtiğiniz tarih henüz gelmediği için en son kur kullanıldı.";
      } else if (usedDate !== toIsoDate(date)) {
        note = "Hafta sonu veya resmi tatil nedeniyle " + toLongDate(usedDate) + " tarihinin kuru kullanıldı.";
      }
      return { rate: rate, source: "ECB / Frankfurter", usedDate: usedDate, note: note };
    });
  }

  function resolveRate(date, key, manual) {
    if (manual && manual.trim()) {
      var value = parseAmount(manual);
      return Promise.resolve({
        rate: value,
        source: "Elle girilen kur",
        usedDate: toIsoDate(date),
        note: "Kur elle girildiği için internet kullanılmadı."
      });
    }
    if (key && key.trim()) {
      return fetchEvdsRate(date, key.trim()).catch(function (evdsError) {
        return fetchPublicRate(date).then(function (info) {
          info.note = "TCMB EVDS kullanılamadı (" + evdsError.message + ") Açık kur verisi kullanıldı." +
            (info.note ? " " + info.note : "");
          return info;
        });
      });
    }
    return fetchPublicRate(date);
  }

  function setStatus(text, isError) {
    statusLine.textContent = text || "";
    statusLine.classList.toggle("error", Boolean(isError));
  }

  function markInvalid(element) {
    if (element) element.setAttribute("aria-invalid", "true");
  }

  function clearInvalid() {
    Object.keys(fields).forEach(function (name) { fields[name].removeAttribute("aria-invalid"); });
  }

  function showResult(info, name, euroAmount, iban) {
    var total = euroAmount * info.rate;
    var generated = buildMessage(name, total, iban);
    rateValue.textContent = "1 EUR = " + formatRate(info.rate) + " TRY";
    rateSource.textContent = info.source;
    convertedValue.textContent = formatMoney(total) + " TL";
    usedDate.textContent = "Kur tarihi: " + toLongDate(info.usedDate);
    rateNote.textContent = info.note || "";
    rateNote.hidden = !info.note;
    message.value = generated;
    copyFeedback.textContent = "";
    result.hidden = false;
    setStatus("Mesaj hazır. Kur kaynağı: " + info.source + ".");
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    clearInvalid();
    setStatus("");
    copyFeedback.textContent = "";

    var date, amount, name, iban;
    try {
      date = parseDate(fields.date.value);
      amount = parseAmount(fields.amount.value);
      name = (fields.name.value || "").trim();
      if (!name) { markInvalid(fields.name); fail("Lütfen adı girin."); }
      iban = fields.iban.value;
    } catch (error) {
      setStatus(error.message, true);
      return;
    }

    generateButton.disabled = true;
    generateButton.querySelector(".button-label").textContent = "Kur alınıyor…";
    setStatus("Seçtiğiniz tarihin kurunu alıyoruz…");

    resolveRate(date, fields.key.value, fields.manual.value).then(function (info) {
      showResult(info, name, amount, iban);
    }).catch(function (error) {
      result.hidden = true;
      setStatus((error && error.message) || "Kur alınamadı. Kur alanına elle yazabilirsiniz.", true);
    }).finally(function () {
      generateButton.disabled = false;
      generateButton.querySelector(".button-label").textContent = "Kuru al ve mesajı oluştur";
    });
  });

  clearButton.addEventListener("click", function () {
    form.reset();
    result.hidden = true;
    clearInvalid();
    copyFeedback.textContent = "";
    setStatus("");
    fields.date.focus();
  });

  copyButton.addEventListener("click", function () {
    var text = message.value;
    if (!text) return;
    var done = function () {
      copyFeedback.textContent = "Kopyalandı ✓";
      setTimeout(function () { copyFeedback.textContent = ""; }, 2200);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done).catch(function () {
        message.select();
        done();
      });
    } else {
      message.select();
      done();
    }
  });

  Object.keys(fields).forEach(function (name) {
    fields[name].addEventListener("input", function () {
      fields[name].removeAttribute("aria-invalid");
    });
  });

  var now = new Date();
  fields.date.value = pad(now.getDate()) + "-" + pad(now.getMonth() + 1) + "-" + now.getFullYear();
})();
