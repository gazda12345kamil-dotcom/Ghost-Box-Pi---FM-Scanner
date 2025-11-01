```markdown
# 📻 Ghost Box Pi - Skaner Radiowy (FM/AM/AIR)

Aplikacja do skanowania pasm radiowych (FM, AM, AIR, CB i więcej) wykorzystująca **RTL-SDR v4** na **Raspberry Pi**. Ghost Box Pi umożliwia automatyczne przełączanie między stacjami radiowymi z regulowaną prędkością, głośnością i zaawansowaną kontrolą szumów.

---

## 📦 Dostępne wersje

Projekt zawiera **trzy wersje** aplikacji do wyboru:

### 1️⃣ Wersja Podstawowa (`ghostbox_fm.py`)

Klasyczna, prosta wersja Ghost Box (tylko FM):

- ✅ Sekwencyjne skanowanie pasma FM (87.5-108 MHz)
- ✅ Regulacja prędkości skanowania (50-500 ms)
- ✅ Kontrola głośności (0-100%)
- ✅ Prosty interfejs (Tkinter)

**Zalecana dla:** Początkujących, którzy chcą prostego działania tylko na FM.

### 2️⃣ Wersja Zaawansowana (`ghostbox_fm_V2.py`)

Rozszerzona wersja (tylko FM) z dodatkowymi funkcjami:

- ✅ Wszystkie funkcje wersji podstawowej
- ✅ Tłumik (Squelch) - automatyczne wyciszanie szumów
- ✅ Tryb Mix (Losowy) - skanowanie FM w losowej kolejności
- ✅ Lepsza kontrola nad dźwiękiem

**Zalecana dla:** Użytkowników, którzy chcą zaawansowanej kontroli skanowania tylko na paśmie FM.

### 3️⃣ Wersja PRO (v4) (`ghostbox_pi_PRO_v4.py`)

W pełni przebudowana, wielopasmowa wersja z nowoczesnym interfejsem:

- ✅ Nowoczesny interfejs (CustomTkinter)
- ✅ Skanowanie Wielu Pasm (FM, AM, AIR, CB, WX, 2M-HAM)
- ✅ Miksowanie Pasm - wybierz dowolną kombinację pasm do skanowania (np. FM + AIR)
- ✅ Zaawansowany Tłumik (Squelch) - precyzyjny tłumik oparty na mocy sygnału po filtracji
- ✅ Wiele Demodulatorów (WBFM, AM, NBFM) dla najlepszej jakości dźwięku

**Zalecana dla:** Zaawansowanych użytkowników, którzy chcą pełnej kontroli i dostępu do wszystkich pasm.

---

## 🤔 Którą wersję wybrać?

| Cecha | Podstawowa | Zaawansowana (V2) | Wersja PRO (v4) |
|-------|------------|-------------------|-----------------|
| **Łatwość użycia** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Interfejs Graficzny** | Standardowy (Tkinter) | Standardowy (Tkinter) | Nowoczesny (CustomTkinter) |
| **Skanowanie FM** | ✅ | ✅ | ✅ |
| **Skanowanie Wielopasmowe** | ❌ | ❌ | ✅ (AM, AIR, CB...) |
| **Miksowanie Pasm** | ❌ | ❌ | ✅ (Dowolna kombinacja) |
| **Kontrola szumów (Squelch)** | ❌ | ✅ (Podstawowy) | ✅ (Zaawansowany) |
| **Tryb losowy (Mix)** | ❌ | ✅ (Tylko FM) | ✅ (Na wybranych pasmach) |

> 💡 **Rekomendacja:** Jeśli chcesz skanować tylko FM, wybierz **V2**. Jeśli chcesz pełnych możliwości, skanowania AM, AIR i miksowania pasm, wybierz **Wersję PRO (v4)**.

---

## 🛠️ Wymagania sprzętowe

- **Raspberry Pi 5** (zalecane) lub **Raspberry Pi 4**
- **RTL-SDR v4** (dongle USB) - **TYLKO ORYGINAŁ!** ⚠️
- Oficjalny zasilacz Raspberry Pi 5 (5V/5A USB-C)
- Głośnik/słuchawki (HDMI, Jack 3.5mm lub Bluetooth)
- Port USB 3.0 (niebieski) - zalecany dla RTL-SDR

### ⚠️ Gdzie kupić oryginalny RTL-SDR v4?

**BARDZO WAŻNE:** Na rynku jest wiele podróbek RTL-SDR, które mogą nie działać!

**Oficjalne sklepy:**
- 🔗 [Lista autoryzowanych sprzedawców](https://www.rtl-sdr.com/buy-rtl-sdr-dvb-t-dongles/)

**Jak rozpoznać oryginał RTL-SDR Blog v4:**
- ✅ Metalowa obudowa (niebieska lub srebrna)
- ✅ Logo "RTL-SDR Blog" na obudowie
- ✅ Złącze SMA (antena przykręcana)
- ✅ Cena około $35-45 USD (ok. 140-180 PLN)

**Oznaki podróbki:**
- ❌ Brak logo "RTL-SDR Blog"
- ❌ Plastikowa obudowa
- ❌ Cena poniżej $25 USD
- ❌ Sprzedawca nieznany na oficjalnej stronie

---

## 💻 Wymagania systemowe

- **System operacyjny:** Raspberry Pi OS (64-bit) - najnowsza wersja
- **Python:** 3.7 lub nowszy
- **Biblioteki systemowe:**
  - RTL-SDR sterowniki v4
  - PortAudio
  - USB libraries

---

## 📥 Instalacja

### Krok 1: Aktualizacja systemu

Otwórz terminal i wykonaj następujące komendy:

```bash
sudo apt update
sudo apt upgrade -y
```

### Krok 2: Instalacja sterowników RTL-SDR v4

RTL-SDR v4 wymaga specjalnych sterowników kompilowanych ze źródeł.

**Usuń stare sterowniki:**

```bash
sudo apt purge -y ^librtlsdr* ^rtl-sdr*
```

**Usuń pozostałości ręcznie:**

```bash
sudo rm -rvf /usr/lib/librtlsdr* /usr/include/rtl-sdr* /usr/local/lib/librtlsdr* /usr/local/include/rtl-sdr* /usr/local/include/rtl_* /usr/local/bin/rtl_*
```

**Zainstaluj narzędzia kompilacji:**

```bash
sudo apt install -y git cmake build-essential libusb-1.0-0-dev pkg-config
```

**Pobierz i skompiluj sterowniki:**

```bash
# Pobierz kod źródłowy
git clone https://github.com/rtlsdrblog/rtl-sdr-blog
cd rtl-sdr-blog

# Przygotuj kompilację
mkdir build
cd build
cmake ../ -DINSTALL_UDEV_RULES=ON -DDETACH_KERNEL_DRIVER=ON

# Skompiluj (może potrwać kilka minut)
make

# Zainstaluj
sudo make install
sudo cp ../rtl-sdr.rules /etc/udev/rules.d/
sudo ldconfig
```

**Zablokuj domyślny sterownik DVB:**

```bash
echo 'blacklist dvb_usb_rtl28xxu' | sudo tee /etc/modprobe.d/blacklist-rtl-sdr.conf
```

**Restart systemu:**

```bash
sudo reboot
```

### Krok 3: Sprawdzenie instalacji

Po restarcie podłącz RTL-SDR v4 do portu USB i wykonaj test:

```bash
rtl_test -t
```

**Oczekiwany wynik:** Powinieneś zobaczyć informacje o urządzeniu (np. “RTL-SDR Blog V4”) i test zakończony pomyślnie.

### Krok 4: Instalacja Pythona i PIP

```bash
sudo apt install -y python3-pip
```

### Krok 5: Instalacja zależności audio

```bash
sudo apt install -y libportaudio2 portaudio19-dev
```

### Krok 6: Instalacja bibliotek Pythona

Wybierz zestaw bibliotek w zależności od wersji, którą chcesz uruchomić.

**A) Dla Wersji Podstawowej (v1) oraz Zaawansowanej (v2):**

```bash
pip install pyrtlsdr sounddevice numpy scipy --break-system-packages
```

**B) Dla Wersji PRO (v4):**

```bash
pip install pyrtlsdr sounddevice numpy scipy customtkinter --break-system-packages
```

**Instalowane biblioteki:**

- `pyrtlsdr` - komunikacja z RTL-SDR
- `sounddevice` - odtwarzanie audio
- `numpy` - operacje numeryczne
- `scipy` - przetwarzanie sygnałów
- `customtkinter` - (TYLKO DLA V4) nowoczesny interfejs graficzny

### Krok 7: Pobranie aplikacji

```bash
# Wróć do katalogu domowego
cd ~

# Sklonuj repozytorium
git clone https://github.com/gazda12345kamil-dotcom/ghost-box-pi.git
cd ghost-box-pi
```

Lub pobierz kod ręcznie i zapisz jako `ghostbox_fm.py` (podstawowa), `ghostbox_fm_V2.py` (zaawansowana) lub `ghostbox_pi_PRO_v4.py` (PRO).

-----

## 🚀 Uruchomienie

**Wersja Podstawowa:**

```bash
python3 ghostbox_fm.py
```

**Wersja Zaawansowana (V2):**

```bash
python3 ghostbox_fm_V2.py
```

**Wersja PRO (v4):**

```bash
python3 ghostbox_pi_PRO_v4.py
```

-----

## 🎛️ Interfejs użytkownika

### 🎯 Wersja Podstawowa (`ghostbox_fm.py`)

- **Wyświetlacz częstotliwości** - aktualna skanowana częstotliwość FM
- **Suwak Prędkości** (50-500 ms)
- **Suwak Głośności** (0-100%)
- **Przyciski START/STOP**
- **Okno logów**

### 🎯 Wersja Zaawansowana (`ghostbox_fm_V2.py`)

Zawiera wszystkie funkcje wersji podstawowej plus:

- **Suwak Tłumika (Squelch)** - próg siły sygnału (0-100)
- **Checkbox “Mix (Losowo)”** - przełącza tryb sekwencyjny/losowy (tylko FM)

### 🎯 Wersja PRO (v4) (`ghostbox_pi_PRO_v4.py`)

- **Nowoczesny Wyświetlacz** - pokazuje częstotliwość i tryb (AM/FM/NBFM)
- **Checkboxy Pasm** - Wybierz pasma do miksowania (FM, AM, AIR, CB, WX, 2M-HAM)
- **Suwak Prędkości** (50-500 ms)
- **Suwak Głośności** (0-100%)
- **Zaawansowany Suwak Tłumika (Squelch)** - precyzyjny próg mocy (0-100)
- **Checkbox “Mix (Losowo)”** - włącza tryb losowy dla wszystkich wybranych pasm
- **Przyciski START/STOP**
- **Okno logów**

-----

## 🔧 Rozwiązywanie problemów

### Problem 1: RTL-SDR nie jest wykrywany

**Rozwiązanie:**

- Sprawdź połączenie USB - użyj portu USB 3.0 (niebieskiego)
- Weryfikuj w systemie: `lsusb` - szukaj ID `0bda:2838`
- Sprawdź zasilanie - używaj oficjalnego zasilacza 5V/5A
- Sprawdź czy masz [oryginał](https://www.rtl-sdr.com/buy-rtl-sdr-dvb-t-dongles/)
- Odłącz i podłącz ponownie dongla
- Sprawdź blacklist: `cat /etc/modprobe.d/blacklist-rtl-sdr.conf`

### Problem 2: Brak dźwięku

**Rozwiązanie:**

- Wybierz wyjście audio: Kliknij prawym przyciskiem ikonę głośnika na pasku zadań i wybierz (HDMI, Headphones, Bluetooth)
- Sprawdź głośność systemową: Kliknij lewym przyciskiem ikonę głośnika

### Problem 3: Błędy podczas instalacji bibliotek

**Rozwiązanie:**

- Upewnij się, że zainstalowano wszystkie zależności systemowe (Krok 2 i 5)
- Sprawdź połączenie internetowe
- Zaktualizuj pip: `pip install --upgrade pip --break-system-packages`
- Ponów instalację bibliotek (Krok 6)

### Problem 4: “Device or resource busy”

**Rozwiązanie:**

- Zamknij wszystkie programy SDR (SDR++, GQRX, CubicSDR)
- Odłącz i podłącz ponownie dongla

### Problem 5: Wersja V2/V4 - Słyszę tylko ciszę

**Rozwiązanie:**

- Sprawdź suwak Tłumika (Squelch) - jeśli jest ustawiony wysoko, może wyciszać wszystkie sygnały
- Ustaw Tłumik na 0 (całkowicie w lewo), aby wyłączyć funkcję
- Stopniowo zwiększaj wartość, aż przestaniesz słyszeć szumy między stacjami

### Problem 6: Błąd przy starcie V4: “No module named ‘customtkinter’”

**Rozwiązanie:**

Nie zainstalowałeś dodatkowej biblioteki dla Wersji PRO. Wykonaj polecenie:

```bash
pip install customtkinter --break-system-packages
```

-----

## ✨ Funkcje

### Wersja Podstawowa:

- ✅ Skanowanie pełnego pasma FM (87.5-108 MHz)
- ✅ Regulowana prędkość skanowania
- ✅ Kontrola głośności
- ✅ Interfejs graficzny (Tkinter)

### Wersja Zaawansowana (V2) - wszystko powyżej plus:

- ✅ Tłumik (Squelch) - wyciszanie szumów na FM
- ✅ Tryb Mix (Losowy) - skanowanie FM w losowej kolejności

### Wersja PRO (v4) - wszystkie funkcje V2 plus:

- ✅ Nowoczesny Interfejs (CustomTkinter)
- ✅ Skanowanie Wielu Pasm (WBFM, AM, NBFM)
- ✅ Pełne Miksowanie Pasm (wybór checkboxami)
- ✅ Zaawansowane Filtrowanie DSP dla każdego trybu
- ✅ Precyzyjny Tłumik (Squelch) oparty na mocy sygnału

-----

## ⚙️ Konfiguracja

Parametry można dostosować bezpośrednio w plikach `.py`.

### Wersje v1 i v2 (`ghostbox_fm.py`, `ghostbox_fm_V2.py`):

```python
# Zakres częstotliwości FM
FM_START_FREQ = 87.5e6
FM_END_FREQ = 108.0e6
FM_STEP = 0.1e6  # Krok skanowania

# Parametry SDR
SDR_SAMPLE_RATE = 1.024e6
SDR_GAIN = 'auto'
AUDIO_SAMPLE_RATE = 48000
```

### Wersja PRO v4 (`ghostbox_pi_PRO_v4.py`):

```python
# Definicje Pasm (WBFM, AM, NBFM)
BANDS_CONFIG = {
    "FM":      {'name': "FM",  'start': 87.5e6,  'end': 108.0e6, 'step': 0.1e6,  'mode': "WBFM"},
    "AIR":     {'name': "AIR", 'start': 108.1e6, 'end': 137.0e6, 'step': 0.025e6, 'mode': "AM"},
    "CB":      {'name': "CB",  'start': 26.965e6,'end': 27.405e6,'step': 0.01e6, 'mode': "AM"},
    "AM":      {'name': "AM", 'start': 531e3,   'end': 1701e3,  'step': 9e3,    'mode': "AM"},
    "WX":      {'name': "WX",  'start': 162.400e6,'end': 162.550e6,'step': 0.025e6,'mode': "NBFM"},
    "2M-HAM":  {'name': "2M-HAM",'start': 144.0e6, 'end': 146.0e6, 'step': 0.025e6,'mode': "NBFM"}
}

# Parametry SDR
SDR_SAMPLE_RATE = 1.024e6
SDR_GAIN = 'auto'
AUDIO_SAMPLE_RATE = 48000
```

-----

## 📚 Wymagane biblioteki

### Python

- `tkinter` - (dla v1, v2) interfejs graficzny
- `pyrtlsdr` - interfejs RTL-SDR
- `sounddevice` - odtwarzanie audio
- `numpy` - obliczenia numeryczne
- `scipy` - przetwarzanie sygnałów
- `customtkinter` - (dla v4) nowoczesny interfejs graficzny

### Systemowe

- `librtlsdr` - sterowniki RTL-SDR v4
- `libportaudio2` - biblioteka audio
- `libusb-1.0-0` - komunikacja USB

-----

## 📄 Licencja

**Open Source** - Ten projekt jest wolnym oprogramowaniem. Każdy może go używać, modyfikować i dystrybuować bez ograniczeń. Kod jest udostępniony publicznie w celach edukacyjnych i społecznościowych.

-----

## ⚠️ Zastrzeżenia

- Aplikacja jest przeznaczona do celów edukacyjnych i eksperymentalnych
- Przestrzegaj lokalnych przepisów dotyczących używania urządzeń radiowych
- Autor nie ponosi odpowiedzialności za niewłaściwe użycie aplikacji

-----

## 📧 Kontakt

W razie pytań lub problemów otwórz **Issue** na GitHubie.

🔗 **Więcej informacji o RTL-SDR:** [www.rtl-sdr.com](https://www.rtl-sdr.com)

-----

**Zbudowano z ❤️ dla społeczności Raspberry Pi i SDR**

```

```
