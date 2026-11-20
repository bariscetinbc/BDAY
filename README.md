# Doğum Günü Hediyesi / Birthday Gift

Tarih, ad, euro tutarı ve isteğe bağlı IBAN ile doğum günü hediye mesajını hazırlayan küçük bir program.

İnternet varsa seçtiğiniz tarihin EUR/TRY kurunu alır, euro tutarını TL'ye çevirir ve şu mesajı oluşturur:

```
Ad iyiki doğdun. Tutar olarak doğum günü hediyemizi yolluyoruz. IBAN
```

## Programı kullanma

| Sistem | Ne yapmalısınız |
| --- | --- |
| Windows | İndirilen `DogumGunuHediyesi-Windows.zip` dosyasını açın, `DogumGunuHediyesi.exe` dosyasına çift tıklayın. Kurulum gerekmez. |
| Mac | İndirilen `DogumGunuHediyesi-Mac.dmg` dosyasını açın, uygulamayı `Applications` klasörüne sürükleyin ve açın. Mac bazen "bilinmeyen geliştirici" uyarısı gösterir; **Aç**'ı seçin. |
| Linux | `python3 main.py` komutunu çalıştırın (GTK 3 gerekir). |
| Hiçbiri | `dist/index.html` dosyasını tarayıcıda açın. İnternet gerekmeden çalışır; kur yazılabilir. |

Alanlar:

- **Tarih** – GG-AA-YYYY (hafta sonu girerseniz önceki iş gününün kuru kullanılır).
- **Ad** – mesajdaki isim.
- **Tutar (EUR)** – hediyenin euro tutarı.
- **IBAN** – isteğe bağlı; boş bırakırsanız mesajda IBAN bölümü olmaz.
- **EVDS anahtarı** – isteğe bağlı. Kişisel TCMB EVDS anahtarınız varsa girin; `TP.DK.EUR.S.YTL` serisi kullanılır.
- **Kur elle** – isteğe bağlı. İnternet yoksa veya kuru kendiniz bilmiyorsanız TRY/EUR değerini yazın; hiç internet isteği yapılmaz.

Kur sırası: elle girilen değer → EVDS anahtarı → açık ECB/Frankfurter verisi.

## Windows ve Mac sürümlerini kendiniz oluşturma

İndirme dosyaları GitHub tarafından otomatik hazırlanır (aşağıya bakın). Kendi bilgisayarınızda oluşturmak isterseniz:

- Windows: Python'u <https://www.python.org/downloads/> adresinden kurun (kurulumda **Add Python to PATH** kutusunu işaretleyin). Sonra `build-windows.bat` dosyasına çift tıklayın. Çıktı: `dist/DogumGunuHediyesi.exe`.
- Mac: Python'u <https://www.python.org/downloads/macos/> adresinden kurun. Terminal'de `chmod +x build-mac.command` yazın, sonra `build-mac.command` dosyasına çift tıklayın. Çıktı: `dist/DogumGunuHediyesi.app`.

## Bunu GitHub'a koyma (adım adım)

1. <https://github.com/new> adresine gidin ve ücretsiz bir hesap açın/zaten giriş yapın.
2. Yeni depo adına örn. `dogum-gunu-hediyesi` yazın. **Public** veya **Private** seçin. "README ile başlat" kutusunu işaretlemeyin.
3. Oluşan sayfadaki **uploading an existing file** bağlantısına tıklayın; bu klasördeki tüm dosyaları (gizli `.github` klasörü dahil) sürükleyip bırakın ve **Commit changes** deyin.
4. **Actions** sekmesini açın. *Build Windows and Mac apps* işi çalışır; bitince en üstteki çalıştırmaya tıklayın ve **Artifacts** bölümünden Windows ve Mac dosyalarını indirin.
5. (İsteğe bağlı) Yeni bir sürüm yayınlamak için **Releases → Draft a new release** bölümünde `v1.0` gibi bir etiket oluşturun. GitHub otomatik olarakWindows ve Mac indirmelerini sürüme ekler.

GitHub'a giriş bu bilgisayarda yapılmadığı için depo şu an yalnızca yerel olarak hazırdır; yayımlama adımını sizin hesabınızdan yapmanız gerekir.

## Geliştirici notları

- `gift_logic.py` – tarih/tutar ayrıştırma, kur sorgulama ve mesaj oluşturma.
- `gift_app.py` – Linux GTK penceresi.
- `gift_app_tk.py` – Windows/macOS Tk penceresi.
- `main.py` – platforma uygun pencereyi açan tek giriş noktası.
- `src/` – tarayıcıda çalışan yerel görünüm.
- `python3 build.py` – `dist/` klasörünü yeniden oluşturur.
- `python3 selftest.py` – 14 hesaplama kontrolünü çalıştırır.

İzin: Kişisel kullanım için hazırlanmıştır. Başkalarına dağıtmadan önce bir lisans eklemeyi düşünün.
