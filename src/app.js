/* BDAY — currency, theme and language aware gift-message tool. */
(function () {
  "use strict";

  var EVDS_BASE = "https://evds3.tcmb.gov.tr/igmevdsms-dis/";
  var FRANKFURTER_BASE = "https://api.frankfurter.dev/v1/";
  var KEY_STORAGE = "dg-evds-key";

  var CURRENCIES = {
    EUR: { evds: "TP.DK.EUR.S.YTL" },
    USD: { evds: "TP.DK.USD.S.YTL" },
    GBP: { evds: "TP.DK.GBP.S.YTL" },
    CHF: { evds: "TP.DK.CHF.S.YTL" }
  };

  var I18N = {
    tr: {
      appTitle: "EVDS Web Servis Kılavuzu",
      language: "Dil",
      theme: "Tema",
      themeLight: "Açık",
      themeDark: "Koyu",
      headingNarrow: "BDAY — Doğum Günü Hediyesi Mesajını Hazırla",
      introNarrow: "Tarih, ad ve tutar zorunludur; IBAN isteğe bağlıdır. TCMB EVDS için kişisel anahtarın varsa HTTP Request Header olarak eklenir; anahtar yoksa Avrupa Merkez Bankası'nın açık kur verisi kullanılır. Tüm tarihler gg-aa-yyyy biçiminde yazılır; hafta sonu ise önceki iş gününün kuru alınır.",
      preferences: "Ayarlar",
      currency: "Para birimi",
      date: "Tarih",
      name: "Ad",
      amount: "Tutar",
      iban: "IBAN",
      optional: "(isteğe bağlı)",
      dateHelp: "GG-AA-YYYY · hafta sonu ise önceki iş gününün kuru kullanılır",
      advanced: "Kur ayarları",
      evdsKey: "TCMB EVDS anahtarı",
      evdsKeyHelp: "Anahtar girilirse TCMB'nin {currency} satış kuru kullanılır.",
      keyRestored: "Kayıtlı anahtar geri yüklendi. Unutana kadar saklanır.",
      forgetKey: "Anahtarı unut",
      keyForgotten: "Kayıtlı anahtar silindi.",
      manualRate: "Kur elle ({currency} / TRY)",
      manualRateHelp: "İnternet yoksa kur buraya yazılabilir; internet kullanılmaz.",
      generate: "Kuru al ve mesajı oluştur",
      generating: "Kur alınıyor…",
      clear: "Temizle",
      fetching: "Seçtiğiniz tarihin kurunu alıyoruz…",
      ready: "Mesaj hazır. Kur kaynağı: {source}.",
      changed: "Para birimi değişti. Mesajı yeniden oluşturun.",
      copied: "Kopyalandı ✓",
      resultHeading: "Hazır mesaj",
      resultIntro: "Kur bilgisi ve gönderilecek metin aşağıda.",
      rate: "Kur",
      converted: "Çevrilen tutar",
      rateDate: "Kur tarihi",
      message: "Mesaj",
      messageHelp: "İstersen metni düzenleyip gönderebilirsin.",
      copy: "Mesajı kopyala",
      hintHeading: "Kur nereden geliyor?",
      hintBody: "TCMB EVDS için kişisel anahtarın varsa onu kullanırız. Anahtar yoksa Avrupa Merkez Bankası'nın açık kur verisi kullanılır. İstersen kur elle de yazabilirsin.",
      msg: "{name} iyiki doğdun. {amount} olarak doğum günü hediyemizi yolluyoruz.",
      sourceEvds: "TCMB EVDS",
      sourcePublic: "ECB / Frankfurter",
      sourceManual: "Elle girilen kur",
      noteFuture: "Seçtiğiniz tarih henüz gelmediği için en son kur kullanıldı.",
      noteWeekend: "Hafta sonu veya resmi tatil nedeniyle {date} tarihinin kuru kullanıldı.",
      noteManual: "Kur elle girildiği için internet kullanılmadı.",
      noteEvdsFail: "TCMB EVDS kullanılamadı ({reason}) Açık kur verisi kullanıldı.",
      errNoDate: "Lütfen bir tarih girin.",
      errBadDate: "Tarihi GG-AA-YYYY biçiminde yazın (örn. 01-05-2024).",
      errDateRange: "Tarih geçerli değil. GG-AA-YYYY biçimini kullanın.",
      errNoCalendar: "Bu tarih takvimde yok (örn. 31-02-2024).",
      errNoAmount: "Lütfen {currency} tutarını girin.",
      errBadAmount: "Tutarı sayı olarak yazın (örn. 25 veya 25,50).",
      errAmountPositive: "Tutar sıfırdan büyük olmalı.",
      errNoName: "Lütfen adı girin.",
      errHttp: "Kur servisi HTTP {status} yanıtı verdi.",
      errTimeout: "Kur servisi zaman aşımına uğradı.",
      errUnreachable: "Kur servisine ulaşılamadı. Kur alanına elle yazabilirsiniz.",
      errEvdsEmpty: "EVDS bu tarih için kur döndürmedi.",
      errPublicValue: "Kur servisinden geçerli bir TRY değeri alınamadı."
    },
    en: {
      appTitle: "EVDS Web Service Guide",
      language: "Language",
      theme: "Theme",
      themeLight: "Light",
      themeDark: "Dark",
      headingNarrow: "BDAY — Prepare your birthday gift message",
      introNarrow: "Date, name and amount are required; IBAN is optional. If you have a personal TCMB EVDS key it is sent as an HTTP request header; otherwise the European Central Bank's public rate is used. Dates are written as dd-mm-yyyy; on a weekend the previous business day's rate is used.",
      preferences: "Settings",
      currency: "Currency",
      date: "Date",
      name: "Name",
      amount: "Amount",
      iban: "IBAN",
      optional: "(optional)",
      dateHelp: "DD-MM-YYYY · on a weekend the previous business day's rate is used",
      advanced: "Exchange-rate settings",
      evdsKey: "TCMB EVDS key",
      evdsKeyHelp: "If a key is entered, the TCMB {currency} selling rate is used.",
      keyRestored: "Saved key restored. It stays saved until you forget it.",
      forgetKey: "Forget key",
      keyForgotten: "Saved key removed.",
      manualRate: "Rate manually ({currency} / TRY)",
      manualRateHelp: "Enter the rate here when offline; no internet request is made.",
      generate: "Get the rate and create the message",
      generating: "Getting the rate…",
      clear: "Clear",
      fetching: "Getting the rate for the selected date…",
      ready: "Message ready. Rate source: {source}.",
      changed: "Currency changed. Please create the message again.",
      copied: "Copied ✓",
      resultHeading: "Ready message",
      resultIntro: "The rate and the text to send are below.",
      rate: "Rate",
      converted: "Converted amount",
      rateDate: "Rate date",
      message: "Message",
      messageHelp: "You may edit the text before sending it.",
      copy: "Copy message",
      hintHeading: "Where does the rate come from?",
      hintBody: "If you have a personal TCMB EVDS key we use it. Otherwise the European Central Bank's public rate is used. You can also type the rate yourself.",
      msg: "Happy birthday, {name}! We are sending your birthday gift of {amount}.",
      sourceEvds: "TCMB EVDS",
      sourcePublic: "ECB / Frankfurter",
      sourceManual: "Entered manually",
      noteFuture: "The selected date is in the future, so the latest rate was used.",
      noteWeekend: "Because of a weekend or holiday, the rate for {date} was used.",
      noteManual: "No internet was used because the rate was entered manually.",
      noteEvdsFail: "TCMB EVDS was unavailable ({reason}); public rate data was used.",
      errNoDate: "Please enter a date.",
      errBadDate: "Write the date as DD-MM-YYYY (e.g. 01-05-2024).",
      errDateRange: "Invalid date. Use DD-MM-YYYY.",
      errNoCalendar: "That date does not exist (e.g. 31-02-2024).",
      errNoAmount: "Please enter the {currency} amount.",
      errBadAmount: "Write the amount as a number (e.g. 25 or 25.50).",
      errAmountPositive: "The amount must be greater than zero.",
      errNoName: "Please enter the name.",
      errHttp: "The rate service returned HTTP {status}.",
      errTimeout: "The rate service timed out.",
      errUnreachable: "The rate service could not be reached. You can type the rate manually.",
      errEvdsEmpty: "EVDS returned no rate for this date.",
      errPublicValue: "No valid TRY value was returned by the rate service."
    }
  };

  function store(key, value) {
    try { localStorage.setItem(key, value); } catch (error) { /* storage may be blocked */ }
  }
  function read(key) {
    try { return localStorage.getItem(key); } catch (error) { return null; }
  }
  function remove(key) {
    try { localStorage.removeItem(key); } catch (error) { /* storage may be blocked */ }
  }

  function savedKey() { return (read(KEY_STORAGE) || "").trim(); }

  function updateKeyState() {
    var hasKey = Boolean(savedKey());
    if (forgetKeyButton) forgetKeyButton.hidden = !hasKey;
    if (keyState) keyState.hidden = !hasKey;
  }

  function rememberKey(value) {
    var key = (value || "").trim();
    if (key) store(KEY_STORAGE, key);
    else remove(KEY_STORAGE);
    updateKeyState();
  }

  function restoreKey() {
    if (fields.key) fields.key.value = savedKey();
    updateKeyState();
  }

  function forgetSavedKey() {
    remove(KEY_STORAGE);
    if (fields.key) fields.key.value = "";
    updateKeyState();
    setStatus("keyForgotten", null, false);
  }

  var state = {
    lang: read("dg-lang") === "en" ? "en" : "tr",
    currency: CURRENCIES[read("dg-currency")] ? read("dg-currency") : "EUR",
    theme: read("dg-theme") === "dark" || read("dg-theme") === "light"
      ? read("dg-theme")
      : (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
  };

  function t(key, vars) {
    var table = I18N[state.lang] || I18N.tr;
    var text = table[key] !== undefined ? table[key] : (I18N.tr[key] !== undefined ? I18N.tr[key] : key);
    if (vars) {
      Object.keys(vars).forEach(function (name) {
        text = text.split("{" + name + "}").join(String(vars[name]));
      });
    }
    return text;
  }

  function fail(key, vars) {
    var error = new Error(t(key, vars));
    error.i18nKey = key;
    error.i18nVars = vars;
    throw error;
  }

  var form = document.getElementById("giftForm");
  var fields = {
    date: document.getElementById("date"),
    name: document.getElementById("name"),
    amount: document.getElementById("amount"),
    iban: document.getElementById("iban"),
    key: document.getElementById("evdsKey"),
    manual: document.getElementById("manualRate")
  };
  var currencySelect = document.getElementById("currency");
  var languageSelect = document.getElementById("language");
  var languageEcho = document.getElementById("languageEcho");
  var themeToggle = document.getElementById("themeToggle");
  var themeLabel = document.getElementById("themeLabel");
  var themeEcho = document.getElementById("themeEcho");
  var amountSuffix = document.getElementById("amountSuffix");
  var manualRateLabel = document.getElementById("manualRateLabel");
  var evdsKeyHelp = document.getElementById("evdsKeyHelp");
  var keyState = document.getElementById("evdsKeyState");
  var forgetKeyButton = document.getElementById("forgetKey");
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

  var lastResult = null;
  var currentStatus = null;

  function applyTheme(theme) {
    state.theme = theme === "dark" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", state.theme);
    document.documentElement.style.colorScheme = state.theme;
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", state.theme === "dark" ? "#0f1113" : "#3c3c3c");
    themeToggle.setAttribute("aria-checked", state.theme === "dark" ? "true" : "false");
    themeToggle.setAttribute("aria-label", t(state.theme === "dark" ? "themeLight" : "themeDark"));
    var labelKey = state.theme === "dark" ? "themeDark" : "themeLight";
    themeLabel.setAttribute("data-i18n", labelKey);
    themeLabel.textContent = t(labelKey);
    themeEcho.setAttribute("data-i18n", labelKey);
    themeEcho.textContent = t(labelKey);
    store("dg-theme", state.theme);
  }

  function applyCurrency(currency, announce) {
    state.currency = CURRENCIES[currency] ? currency : "EUR";
    currencySelect.value = state.currency;
    amountSuffix.textContent = state.currency;
    manualRateLabel.textContent = t("manualRate", { currency: state.currency });
    evdsKeyHelp.textContent = t("evdsKeyHelp", { currency: state.currency });
    store("dg-currency", state.currency);
    if (announce && lastResult) {
      lastResult = null;
      result.hidden = true;
      setStatus("changed", null, false);
    }
  }

  function applyLanguage(lang) {
    state.lang = lang === "en" ? "en" : "tr";
    document.documentElement.setAttribute("lang", state.lang);
    languageSelect.value = state.lang;
    languageEcho.textContent = state.lang === "en" ? "English" : "Türkçe";
    Array.prototype.forEach.call(document.querySelectorAll("[data-i18n]"), function (element) {
      element.textContent = t(element.getAttribute("data-i18n"));
    });
    applyTheme(state.theme);
    applyCurrency(state.currency, false);
    if (currentStatus) setStatus(currentStatus.key, currentStatus.vars, currentStatus.isError);
    if (lastResult) renderResult(lastResult.info, lastResult.name, lastResult.amount, lastResult.iban);
    store("dg-lang", state.lang);
  }

  function pad(value) { return String(value).padStart(2, "0"); }
  function toEvdsDate(date) { return pad(date.getUTCDate()) + "-" + pad(date.getUTCMonth() + 1) + "-" + date.getUTCFullYear(); }
  function toIsoDate(date) { return date.getUTCFullYear() + "-" + pad(date.getUTCMonth() + 1) + "-" + pad(date.getUTCDate()); }
  function toLongDate(iso) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(iso || "")) return iso || "–";
    var p = iso.split("-");
    return state.lang === "tr" ? p[2] + "." + p[1] + "." + p[0] : p[1] + "/" + p[2] + "/" + p[0];
  }

  function parseDate(text) {
    var value = (text || "").trim().replace(/\s+/g, "");
    if (!value) fail("errNoDate");
    var match = value.match(/^(\d{1,4})[-/.](\d{1,2})[-/.](\d{1,4})$/);
    if (!match) fail("errBadDate");
    var a = Number(match[1]), b = Number(match[2]), c = Number(match[3]);
    var year, month, day;
    if (match[1].length === 4) { year = a; month = b; day = c; }
    else { year = c; day = a; month = b; }
    if (year < 1900 || year > 2200 || month < 1 || month > 12 || day < 1 || day > 31) fail("errDateRange");
    var date = new Date(Date.UTC(year, month - 1, day));
    if (date.getUTCFullYear() !== year || date.getUTCMonth() !== month - 1 || date.getUTCDate() !== day) fail("errNoCalendar");
    return date;
  }

  function previousBusinessDay(date) {
    var day = new Date(date.getTime());
    while (day.getUTCDay() === 0 || day.getUTCDay() === 6) day.setUTCDate(day.getUTCDate() - 1);
    return day;
  }

  function parseAmount(text) {
    var value = (text || "").trim().replace(/\s/g, "");
    if (!value) fail("errNoAmount", { currency: state.currency });
    if (value.indexOf(",") !== -1 && value.indexOf(".") !== -1) {
      if (value.lastIndexOf(",") > value.lastIndexOf(".")) value = value.replace(/\./g, "").replace(",", ".");
      else value = value.replace(/,/g, "");
    } else if (value.indexOf(",") !== -1) {
      value = value.replace(/,/g, ".");
    }
    if (!/^\d+(\.\d+)?$/.test(value)) fail("errBadAmount");
    var amount = Number(value);
    if (!isFinite(amount) || amount <= 0) fail("errAmountPositive");
    return amount;
  }

  function groupInteger(text, lang) {
    var separator = lang === "tr" ? "." : ",";
    return text.replace(/\B(?=(\d{3})+(?!\d))/g, separator);
  }
  function formatMoney(value) {
    var fixed = Math.round(value * 100) / 100;
    var parts = fixed.toFixed(2).split(".");
    return groupInteger(parts[0], state.lang) + (state.lang === "tr" ? "," : ".") + parts[1];
  }
  function formatRate(value) {
    var text = value.toFixed(4).replace(/0+$/, "").replace(/\.$/, "");
    var parts = text.split(".");
    return groupInteger(parts[0], state.lang) + (parts[1] ? (state.lang === "tr" ? "," : ".") + parts[1] : "");
  }

  function buildMessage(name, amountInTry, iban) {
    var beginning = t("msg", { name: (name || "").trim(), amount: formatMoney(amountInTry) });
    var cleanIban = (iban || "").trim();
    return cleanIban ? beginning + " " + cleanIban : beginning;
  }

  function noteText(info) {
    if (!info) return "";
    if (info.noteKey) return t(info.noteKey, info.noteVars);
    return info.note || "";
  }

  function fetchJson(url, options, timeoutMs) {
    var controller = new AbortController();
    var timer = setTimeout(function () { controller.abort(); }, timeoutMs || 9000);
    var settings = Object.assign({ signal: controller.signal, cache: "no-store" }, options || {});
    return fetch(url, settings).then(function (response) {
      if (!response.ok) fail("errHttp", { status: response.status });
      return response.json();
    }).catch(function (error) {
      if (error && error.i18nKey) throw error;
      if (error && error.name === "AbortError") fail("errTimeout");
      fail("errUnreachable");
    }).finally(function () { clearTimeout(timer); });
  }

  function firstPositiveValue(payload) {
    var items = Array.isArray(payload) ? payload : (payload && (payload.data || payload.Items || payload.items)) || [];
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
    var series = CURRENCIES[state.currency].evds;
    var query = "series=" + series +
      "&startDate=" + encodeURIComponent(toEvdsDate(date)) +
      "&endDate=" + encodeURIComponent(toEvdsDate(date)) +
      "&type=json";
    return fetchJson(EVDS_BASE + query, { headers: { key: key, Accept: "application/json" } }, 8000)
      .then(function (payload) {
        var rate = firstPositiveValue(payload);
        if (rate === null) fail("errEvdsEmpty");
        return { rate: rate, source: "evds", usedDate: toIsoDate(date), note: "" };
      });
  }

  function fetchPublicRate(date) {
    var today = new Date();
    var isFuture = toIsoDate(date) > toIsoDate(new Date(Date.UTC(today.getFullYear(), today.getMonth(), today.getDate())));
    var wantedDate = isFuture ? null : previousBusinessDay(date);
    var url = isFuture
      ? FRANKFURTER_BASE + "latest?base=" + state.currency + "&symbols=TRY"
      : FRANKFURTER_BASE + toIsoDate(wantedDate) + "?base=" + state.currency + "&symbols=TRY";
    return fetchJson(url, null, 10000).then(function (payload) {
      var rate = payload && payload.rates ? Number(payload.rates.TRY) : NaN;
      if (!isFinite(rate) || rate <= 0) fail("errPublicValue");
      var usedDate = (payload && payload.date) || toIsoDate(date);
      var noteKey = "";
      var noteVars = null;
      var note = "";
      if (isFuture) {
        noteKey = "noteFuture";
        note = t(noteKey);
      } else if (usedDate !== toIsoDate(date)) {
        noteKey = "noteWeekend";
        noteVars = { date: toLongDate(usedDate) };
        note = t(noteKey, noteVars);
      }
      return { rate: rate, source: "public", usedDate: usedDate, note: note, noteKey: noteKey, noteVars: noteVars };
    });
  }

  function resolveRate(date, key, manual) {
    if (manual && manual.trim()) {
      return Promise.resolve({
        rate: parseAmount(manual),
        source: "manual",
        usedDate: toIsoDate(date),
        note: t("noteManual"),
        noteKey: "noteManual",
        noteVars: null
      });
    }
    if (key && key.trim()) {
      return fetchEvdsRate(date, key.trim()).catch(function (error) {
        var reason = error && error.i18nKey ? t(error.i18nKey, error.i18nVars) : (error && error.message) || "";
        return fetchPublicRate(date).then(function (info) {
          info.note = t("noteEvdsFail", { reason: reason }) + (info.note ? " " + info.note : "");
          info.noteKey = "";
          info.noteVars = null;
          return info;
        });
      });
    }
    return fetchPublicRate(date);
  }

  function setStatus(key, vars, isError) {
    currentStatus = key ? { key: key, vars: vars || null, isError: Boolean(isError) } : null;
    statusLine.textContent = key ? t(key, vars) : "";
    statusLine.classList.toggle("error", Boolean(isError));
  }

  function markInvalid(element) { if (element) element.setAttribute("aria-invalid", "true"); }
  function clearInvalid() { Object.keys(fields).forEach(function (name) { fields[name].removeAttribute("aria-invalid"); }); }

  function renderResult(info, name, euroAmount, iban) {
    var total = euroAmount * info.rate;
    rateValue.textContent = "1 " + state.currency + " = " + formatRate(info.rate) + " TRY";
    rateSource.textContent = t(info.source === "evds" ? "sourceEvds" : info.source === "manual" ? "sourceManual" : "sourcePublic");
    convertedValue.textContent = formatMoney(total) + " TL";
    usedDate.textContent = t("rateDate") + ": " + toLongDate(info.usedDate);
    rateNote.textContent = noteText(info);
    rateNote.hidden = !info.note;
    message.value = buildMessage(name, total, iban);
    copyFeedback.textContent = "";
    result.hidden = false;
    setStatus("ready", { source: rateSource.textContent }, false);
  }

  function showResult(info, name, amount, iban) {
    lastResult = { info: info, name: name, amount: amount, iban: iban };
    renderResult(lastResult.info, lastResult.name, lastResult.amount, lastResult.iban);
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    clearInvalid();
    setStatus(null);
    copyFeedback.textContent = "";
    var date, amount, name, iban;
    try {
      date = parseDate(fields.date.value);
      amount = parseAmount(fields.amount.value);
      name = (fields.name.value || "").trim();
      if (!name) { markInvalid(fields.name); fail("errNoName"); }
      iban = fields.iban.value;
    } catch (error) {
      setStatus(error.i18nKey || "errUnreachable", error.i18nVars, true);
      return;
    }
    generateButton.disabled = true;
    generateButton.querySelector(".button-label").textContent = t("generating");
    setStatus("fetching");
    resolveRate(date, fields.key.value, fields.manual.value).then(function (info) {
      showResult(info, name, amount, iban);
    }).catch(function (error) {
      lastResult = null;
      result.hidden = true;
      setStatus(error && error.i18nKey ? error.i18nKey : "errUnreachable", error && error.i18nVars, true);
    }).finally(function () {
      generateButton.disabled = false;
      generateButton.querySelector(".button-label").textContent = t("generate");
    });
  });

  clearButton.addEventListener("click", function () {
    form.reset();
    result.hidden = true;
    lastResult = null;
    clearInvalid();
    copyFeedback.textContent = "";
    setStatus(null);
    restoreKey(); /* clearing the form must not remove a saved key */
    applyCurrency(state.currency, false);
    applyLanguage(state.lang);
    fields.date.focus();
  });

  if (forgetKeyButton) forgetKeyButton.addEventListener("click", forgetSavedKey);

  copyButton.addEventListener("click", function () {
    var text = message.value;
    if (!text) return;
    var done = function () {
      copyFeedback.textContent = t("copied");
      setTimeout(function () { copyFeedback.textContent = ""; }, 2200);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done).catch(function () { message.select(); done(); });
    } else {
      message.select();
      done();
    }
  });

  currencySelect.addEventListener("change", function () { applyCurrency(currencySelect.value, true); });
  languageSelect.addEventListener("change", function () { applyLanguage(languageSelect.value); });
  themeToggle.addEventListener("click", function () {
    applyTheme(state.theme === "dark" ? "light" : "dark");
    if (lastResult) setStatus(currentStatus && currentStatus.key, currentStatus && currentStatus.vars, currentStatus && currentStatus.isError);
  });

  Object.keys(fields).forEach(function (name) {
    fields[name].addEventListener("input", function () { fields[name].removeAttribute("aria-invalid"); });
  });
  fields.key.addEventListener("input", function () { rememberKey(fields.key.value); });

  var now = new Date();
  fields.date.value = pad(now.getDate()) + "-" + pad(now.getMonth() + 1) + "-" + now.getFullYear();
  restoreKey();
  applyLanguage(state.lang);
})();
