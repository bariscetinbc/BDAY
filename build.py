"""Build BDAY into app/dist.

The preview entry point is a working gift-message tool (index.html), not a PDF
viewer. The same logic is also shipped as a native Python/GTK desktop program.
"""

from pathlib import Path
import shutil

root = Path(__file__).resolve().parent
source = root / "src"
output = root / "dist"

if output.exists():
    shutil.rmtree(output)
output.mkdir(parents=True)

for name in ("index.html", "styles.css", "app.js"):
    shutil.copy2(source / name, output / name)

for name in ("gift_logic.py", "gift_app.py", "gift_app_tk.py", "main.py", "selftest.py"):
    shutil.copy2(root / name, output / name)

launcher = output / "bday.sh"
launcher.write_text(
    "#!/bin/sh\n"
    'cd "$(dirname "$0")" || exit 1\n'
    'exec python3 gift_app.py "$@"\n',
    encoding="utf-8",
)
launcher.chmod(0o755)

desktop = output / "bday.desktop"
desktop.write_text(
    "[Desktop Entry]\n"
    "Type=Application\n"
    "Name=BDAY\n"
    "Comment=Euro tutarını seçilen tarihin kuruna çevirip hediye mesajı hazırlar\n"
    "Exec=python3 gift_app.py\n"
    "Terminal=false\n"
    "Categories=Utility;\n",
    encoding="utf-8",
)

(output / "OKUMA-BENI.txt").write_text(
    "BDAY\n"
    "===================\n\n"
    "index.html dosyasını tarayıcıda açın: tarih, ad, seçtiğiniz para biriminin tutarı\n"
    "ve isteğe bağlı IBAN ile mesajı hazırlar. Para birimi (EUR/USD/GBP/CHF), dil\n"
    "(Türkçe/English) ve açık/koyu tema üstteki ayarlardan seçilir ve hatırlanır.\n"
    "Kur TCMB EVDS (anahtarınız varsa), yoksa açık ECB verisi veya elle girdiğiniz\n"
    "değerden alınır. Mesaj seçilen dilde hazırlanır. EVDS anahtarınızı girdiğinizde\n"
    "sonraki açılışlarda geri yüklenir; 'Anahtarı unut' ile silinene kadar saklanır.\n\n"
    "Masaüstünde çalıştırmak için bday.sh dosyasını açın (Linux: Python 3 + GTK 3).\n"
    "Windows için build-windows.bat, Mac için build-mac.command dosyası kendi başına çalıştırılabilir\n"
    "program hazırlar. Ayrıntılar README.md dosyasındadır.\n",
    encoding="utf-8",
)

print("Built BDAY into app/dist")
