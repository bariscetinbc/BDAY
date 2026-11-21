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
| Windows | İndirilen `BDAY-Windows.zip` dosyasını açın, `BDAY.exe` dosyasına çift tıklayın. Kurulum gerekmez. |
| Mac | İndirilen `BDAY-Mac.dmg` dosyasını açın, uygulamayı `Applications` klasörüne sürükleyin ve açın. Mac bazen "bilinmeyen geliştirici" uyarısı gösterir; **Aç**'ı seçin. |
| Linux | `python3 main.py` komutunu çalıştırın (GTK 3 gerekir). |
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

## GitHub deposu

Proje <https://github.com/bariscetinbc/BDAY> adresinde yayımlanmak üzere hazırdır. Bu bilgisayarda GitHub girişi olmadığı için ilk yükleme sizin hesabınızdan yapılmalıdır.

En kolay yol: bu klasörde `./publish.sh` dosyasını çalıştırın. GitHub CLI ile giriş yapmanızı ister, `BDAY` deposunu hesabınızda açar ve kodu yükler. Zaten giriş yaptıysanız tek adımda yüklemeyi tamamlar.

Elle yapmak isterseniz:

1. <https://github.com/new> adresine gidin, depo adına `BDAY` yazın, **Public** veya **Private** seçin ve "README ile başlat" kutusunu işaretlemeyin.
2. Bilgisayarda şu komutları çalıştırın: `gh auth login`, ardından `gh repo create bariscetinbc/BDAY --public --source=. --remote=origin --push` (depoyu siz açtıysanız ikinci komut yerine `git push -u origin main` yeterli).
3. **Actions** sekmesini açın. *Build BDAY for Windows and Mac* işi çalışır; bitince en üstteki çalıştırmaya tıklayın ve **Artifacts** bölümünden Windows ve Mac dosyalarını indirin.
4. (İsteğe bağlı) Yeni bir sürüm yayınlamak için **Releases → Draft a new release** bölümünde `v1.0` gibi bir etiket oluşturun. GitHub otomatik olarak Windows ve Mac indirmelerini sürüme ekler.

## Geliştirici notları

- `gift_logic.py` – tarih/tutar ayrıştırma, kur sorgulama ve mesaj oluşturma.
- `gift_app.py` – Linux GTK penceresi.
- `gift_app_tk.py` – Windows/macOS Tk penceresi.
- `main.py` – platforma uygun pencereyi açan tek giriş noktası.
- `src/` – tarayıcıda çalışan yerel görünüm.
- `python3 build.py` – `dist/` klasörünü yeniden oluşturur.
- `python3 selftest.py` – 26 hesaplama, mesaj ve ayar kontrolünü çalıştırır.

İzin: Kişisel kullanım için hazırlanmıştır. Başkalarına dağıtmadan önce bir lisans eklemeyi düşünün.
