# BDAY

BDAY hazır bir doğum günü hediye mesajı oluşturur: tarih, ad, para birimi tutarı ve isteğe bağlı IBAN yazarsınız; seçtiğiniz tarihin kurunu alıp tutarı TL'ye çevirir ve mesajı hazırlar.

Yeni: **para birimi seçimi** (EUR / USD / GBP / CHF), **Türkçe / İngilizce dil seçimi** ve **açık / koyu tema** anahtarı. Bu üç seçim hatırlanır; bir sonraki açılışta aynı ayarlarla başlar.

İnternet varsa seçtiğiniz tarihin seçili para birimi / TRY kurunu alır, tutarı TL'ye çevirir ve şu mesajı oluşturur:

```
Ad iyiki doğdun. Tutar olarak doğum günü hediyemizi yolluyoruz. IBAN
```

İngilizce seçilirse mesaj şu biçimde olur:

```
Happy birthday, Name! We are sending your birthday gift of Tutar. IBAN
```

Dil değiştirildiğinde hazır mesaj da yeni dilde yeniden yazılır.

## Programı kullanma

| Sistem | Ne yapmalısınız |
| --- | --- |
| Windows | [BDAY-Windows.zip](https://github.com/bariscetinbc/BDAY/releases/latest/download/BDAY-Windows.zip) dosyasını indirin, açın ve `BDAY.exe` dosyasına çift tıklayın. Kurulum gerekmez. Hazır kopya ayrıca `downloads/Windows/BDAY-Windows.zip` içinde duruyor. |
| Mac | [BDAY-Mac.dmg](https://github.com/bariscetinbc/BDAY/releases/latest/download/BDAY-Mac.dmg) dosyasını indirin, açın ve uygulamayı `Applications` klasörüne sürükleyin. Hazır kopya ayrıca `downloads/Mac/BDAY-Mac.dmg` içinde duruyor. Mac bazen "bilinmeyen geliştirici" uyarısı gösterir; **Aç**'ı seçin. |
| Linux | [BDAY-Linux.tar.gz](https://github.com/bariscetinbc/BDAY/releases/latest/download/BDAY-Linux.tar.gz) dosyasını indirin, açın ve `BDAY` dosyasına çift tıklayın. Python kurulumu gerekmez. Hazır kopya ayrıca `downloads/Linux/BDAY-Linux.tar.gz` içinde duruyor. |
| Hiçbiri | `dist/index.html` dosyasını tarayıcıda açın. İnternet gerekmeden çalışır; kur yazılabilir. |

Alanlar:

- **Tarih** – GG-AA-YYYY (hafta sonu girerseniz önceki iş gününün kuru kullanılır).
- **Ad** – mesajdaki isim.
- **Para birimi** – EUR, USD, GBP veya CHF. Kur bu birim için alınır.
- **Tutar** – hediyenin seçili para birimindeki tutarı.
- **IBAN** – isteğe bağlı; boş bırakırsanız mesajda IBAN bölümü olmaz.
- **Dil** – Türkçe veya English; hem arayüzü hem de oluşturulan mesajı değiştirir.
- **Tema** – açık veya koyu görünüm.
- **EVDS anahtarı** – isteğe bağlı. Kişisel TCMB EVDS anahtarınız varsa girin; seçili para biriminin satış kuru serisi kullanılır. Anahtar kaydedilir ve sonraki açılışta geri yüklenir; **Anahtarı unut** düğmesiyle silinene kadar saklanır. Tarayıcı önizlemesinde anahtar tarayıcının yerel deposunda, masaüstü programlarında küçük bir ayarlar dosyasında tutulur.
- **Kur elle** – isteğe bağlı. İnternet yoksa veya kuru kendiniz biliyorsanız seçili para birimi / TRY değerini yazın; hiç internet isteği yapılmaz.

Kur sırası: elle girilen değer → EVDS anahtarı → açık ECB/Frankfurter verisi. EVDS serisi seçilen birime göre `TP.DK.EUR.S.YTL`, `TP.DK.USD.S.YTL`, `TP.DK.GBP.S.YTL` veya `TP.DK.CHF.S.YTL` olur. Dört seri kodu ve adı TCMB'nin yayımladığı `bie_dkdovytl` veri grubu kataloğunda doğrulanmıştır; gerçek bir kişisel anahtarla canlı kur sorgusu ise anahtar sağlanmadığı için sizin tarafınızdan denenebilir. Kişisel anahtar olmadan tarayıcı önizlemesi açık ECB verisini kullanır.

## Windows ve Mac sürümlerini kendiniz oluşturma

İndirme dosyaları GitHub tarafından otomatik hazırlanır (aşağıya bakın). Kendi bilgisayarınızda oluşturmak isterseniz:

- Windows: Python'u <https://www.python.org/downloads/> adresinden kurun (kurulumda **Add Python to PATH** kutusunu işaretleyin). Sonra `build-windows.bat` dosyasına çift tıklayın. Çıktı: `dist/BDAY.exe`.
- Mac: Python'u <https://www.python.org/downloads/macos/> adresinden kurun. Terminal'de `chmod +x build-mac.command` yazın, sonra `build-mac.command` dosyasına çift tıklayın. Çıktı: `dist/BDAY.app`.
- Linux: Python 3 ve PyInstaller kuruluysa `python3 build_linux.py` komutunu çalıştırın. Çıktı: `downloads/Linux/BDAY-Linux.tar.gz`. GTK 3 penceresi sistemde hazır olmalıdır (Debian/Ubuntu: `sudo apt install libgtk-3-0`).

## GitHub deposu

Proje <https://github.com/bariscetinbc/BDAY> adresinde yayımlandı. Windows ve Mac programları GitHub Actions ile oluşturuldu; indirme dosyaları `downloads/` klasöründe de hazır duruyor.

GitHub'daki **Releases** bölümünden en son sürümü açarsanız `BDAY-Windows.zip`, `BDAY-Mac.dmg` ve `BDAY-Linux.tar.gz` dosyalarını doğrudan indirebilirsiniz. Kodda değişiklik yapıp yüklemek isterseniz `git push -u origin main` yeterli; her yüklemede Windows, Mac ve Linux dosyaları yeniden hazırlanır. `v1.1` gibi bir etiket yüklerseniz dosyalar otomatik olarak yeni sürüme eklenir.

## Geliştirici notları

- `gift_logic.py` – tarih/tutar ayrıştırma, kur sorgulama ve mesaj oluşturma.
- `gift_app.py` – Linux GTK penceresi.
- `gift_app_tk.py` – Windows/macOS Tk penceresi.
- `main.py` – platforma uygun pencereyi açan tek giriş noktası.
- `src/` – tarayıcıda çalışan yerel görünüm.
- `python3 build.py` – `dist/` klasörünü yeniden oluşturur.
- `python3 build_linux.py` – indirilebilir Linux programını oluşturur.
- `python3 selftest.py` – 26 hesaplama, mesaj ve ayar kontrolünü çalıştırır.

İzin: Kişisel kullanım için hazırlanmıştır. Başkalarına dağıtmadan önce bir lisans eklemeyi düşünün.
