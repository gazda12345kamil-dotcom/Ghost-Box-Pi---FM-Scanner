# Ghost Box Pi - FM Scanner

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi%205-red.svg)
![License](https://img.shields.io/badge/License-Open%20Source-green.svg)

Aplikacja do skanowania pasma FM (87.5-108 MHz) wykorzystująca RTL-SDR v4 na Raspberry Pi. Ghost Box Pi umożliwia automatyczne przełączanie między stacjami radiowymi z regulowaną prędkością i głośnością.

## 📦 Dostępne wersje

Projekt zawiera **dwie wersje** aplikacji do wyboru:

### 1️⃣ **Wersja Podstawowa** (`ghostbox_fm.py`)
Klasyczna, prosta wersja Ghost Box z podstawowymi funkcjami:
- ✅ Sekwencyjne skanowanie pasma FM (87.5-108 MHz)
- ✅ Regulacja prędkości skanowania (50-500 ms)
- ✅ Kontrola głośności (0-100%)
- ✅ Prosty i przejrzysty interfejs

**Zalecana dla**: Początkujących użytkowników, którzy chcą prostego i stabilnego działania.

---

### 2️⃣ **Wersja Zaawansowana** (`ghostbox_fm_V2.py`)
Rozszerzona wersja z dodatkowymi funkcjami:
- ✅ **Wszystkie funkcje wersji podstawowej**
- ✅ **Tłumik (Squelch)** - automatyczne wyciszanie słabych sygnałów i szumów
- ✅ **Tryb Mix (Losowy)** - skanowanie w losowej kolejności zamiast sekwencyjnej
- ✅ Lepsza kontrola nad jakością dźwięku

**Zalecana dla**: Zaawansowanych użytkowników poszukujących większej kontroli nad działaniem.

---

### 🤔 Którą wersję wybrać?

| Cecha | Podstawowa | Zaawansowana (V2) |
|-------|------------|-------------------|
| Łatwość użycia | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Funkcje | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Kontrola szumów | ❌ | ✅ (Squelch) |
| Tryb losowy | ❌ | ✅ (Mix) |
| Rozmiar okna | 480x420 | 480x480 |

💡 **Rekomendacja**: Zacznij od **wersji podstawowej**, a po oswojeniu się przejdź na **V2** dla większych możliwości.

---

## Wymagania sprzętowe

- **Raspberry Pi 5** (zalecane) lub Raspberry Pi 4
- **RTL-SDR v4** (dongle USB) - **TYLKO ORYGINAŁ!** ⚠️
- **Oficjalny zasilacz** Raspberry Pi 5 (5V/5A USB-C)
- Głośnik/słuchawki (HDMI, Jack 3.5mm lub Bluetooth)
- Port USB 3.0 (niebieski) - zalecany dla RTL-SDR

### ⚠️ Gdzie kupić oryginalny RTL-SDR v4?

**BARDZO WAŻNE**: Na rynku jest wiele podróbek RTL-SDR, które mogą nie działać!

**Oficjalne sklepy:**
- 🔗 **Lista autoryzowanych sprzedawców**: [https://www.rtl-sdr.com/buy-rtl-sdr-dvb-t-dongles/](https://www.rtl-sdr.com/buy-rtl-sdr-dvb-t-dongles/)

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

## Wymagania systemowe

- **System operacyjny**: Raspberry Pi OS (64-bit) - najnowsza wersja
- **Python**: 3.7 lub nowszy
- **Biblioteki systemowe**: 
  - RTL-SDR sterowniki v4
  - PortAudio
  - USB libraries

---

## Instalacja

### Krok 1: Aktualizacja systemu

Otwórz terminal i wykonaj następujące komendy:

```bash
sudo apt update
sudo apt upgrade -y
```

---

### Krok 2: Instalacja sterowników RTL-SDR v4

RTL-SDR v4 wymaga specjalnych sterowników kompilowanych ze źródeł.

**Usuń stare sterowniki:**

```bash
sudo apt purge -y ^librtlsdr* ^rtl-sdr*
```

**Usuń pozostałości ręcznie (skopiuj całą linię dokładnie!):**

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

---

### Krok 3: Sprawdzenie instalacji

Po restarcie podłącz RTL-SDR v4 do portu USB i wykonaj test:

```bash
rtl_test -t
```

**Oczekiwany wynik**: Powinieneś zobaczyć informacje o urządzeniu (np. "RTL-SDR Blog V4") i test zakończony pomyślnie.

---

### Krok 4: Instalacja Pythona i PIP

```bash
sudo apt install -y python3-pip
```

---

### Krok 5: Instalacja zależności audio

```bash
sudo apt install -y libportaudio2 portaudio19-dev
```

---

### Krok 6: Instalacja bibliotek Pythona

```bash
pip install pyrtlsdr sounddevice numpy scipy --break-system-packages
```

**Instalowane biblioteki:**
- `pyrtlsdr` - komunikacja z RTL-SDR
- `sounddevice` - odtwarzanie audio
- `numpy` - operacje numeryczne
- `scipy` - przetwarzanie sygnałów

---

### Krok 7: Pobranie aplikacji

```bash
# Wróć do katalogu domowego
cd ~

# Sklonuj repozytorium
git clone https://github.com/gazda12345kamil-dotcom/ghost-box-pi.git
cd ghost-box-pi
```

Lub pobierz kod ręcznie i zapisz jako `ghostbox_fm.py` (wersja podstawowa) lub `ghostbox_fm_V2.py` (wersja zaawansowana) na pulpicie.

---

## Uruchomienie

### Wersja Podstawowa:

```bash
# Jeśli aplikacja jest na pulpicie
cd ~/Desktop
python3 ghostbox_fm.py

# Jeśli aplikacja jest w folderze z repozytorium
cd ~/ghost-box-pi
python3 ghostbox_fm.py
```

### Wersja Zaawansowana (V2):

```bash
# Jeśli aplikacja jest na pulpicie
cd ~/Desktop
python3 ghostbox_fm_V2.py

# Jeśli aplikacja jest w folderze z repozytorium
cd ~/ghost-box-pi
python3 ghostbox_fm_V2.py
```

---

## Interfejs użytkownika

### 🎯 Wersja Podstawowa (`ghostbox_fm.py`)

Po uruchomieniu zobaczysz okno z:

- **Wyświetlacz częstotliwości** - aktualna skanowana częstotliwość FM
- **Suwak Prędkości** - czas spędzony na jednej częstotliwości (50-500 ms)
- **Suwak Głośności** - kontrola poziomu głośności (0-100%)
- **Przyciski START/STOP** - kontrola skanowania
- **Okno logów** - komunikaty systemowe i diagnostyczne

### 🎯 Wersja Zaawansowana (`ghostbox_fm_V2.py`)

Zawiera wszystkie funkcje wersji podstawowej plus:

- **Suwak Tłumika (Squelch)** - próg siły sygnału (0-100)
  - Wartość 0 = wyłączony (słyszysz wszystko, włącznie z szumami)
  - Wartość 10-30 = standardowe użycie (wycisza słabe sygnały)
  - Wartość 50+ = tylko mocne stacje
- **Checkbox "Mix (Losowo)"** - przełącza między trybem sekwencyjnym a losowym
  - Odznaczone = skanowanie po kolei (87.5 → 87.6 → 87.7...)
  - Zaznaczone = skanowanie losowych częstotliwości

---

## Rozwiązywanie problemów

### Problem 1: RTL-SDR nie jest wykrywany

**Rozwiązanie:**

1. Sprawdź połączenie USB - użyj portu USB 3.0 (niebieskiego)
2. Weryfikuj w systemie: `lsusb` - szukaj ID `0bda:2838`
3. Sprawdź zasilanie - używaj oficjalnego zasilacza 5V/5A
4. Sprawdź czy masz oryginał: [https://www.rtl-sdr.com/buy-rtl-sdr-dvb-t-dongles/](https://www.rtl-sdr.com/buy-rtl-sdr-dvb-t-dongles/)
5. Odłącz i podłącz ponownie dongla
6. Sprawdź blacklist: `cat /etc/modprobe.d/blacklist-rtl-sdr.conf`

---

### Problem 2: Brak dźwięku

**Rozwiązanie:**

1. **Wybierz wyjście audio:**
   - Kliknij prawym przyciskiem ikonę głośnika na pasku zadań
   - Wybierz odpowiednie urządzenie (HDMI, Headphones, Bluetooth)

2. **Sprawdź głośność systemową:**
   - Kliknij lewym przyciskiem ikonę głośnika
   - Upewnij się, że głośność nie jest wyciszona

3. **Test sounddevice:**
   ```python
   python3
   >>> import sounddevice as sd
   >>> import numpy as np
   >>> fs = 48000
   >>> t = np.arange(fs * 3)
   >>> audio = 0.5 * np.sin(2 * np.pi * 440 * t / fs)
   >>> sd.play(audio.astype(np.float32), fs)
   >>> sd.wait()
   >>> exit()
   ```

4. **Użyj pavucontrol (opcjonalnie):**
   ```bash
   sudo apt install pavucontrol
   pavucontrol
   ```

---

### Problem 3: Błędy podczas instalacji bibliotek

**Rozwiązanie:**

1. Upewnij się, że zainstalowano wszystkie zależności systemowe
2. Sprawdź połączenie internetowe
3. Zaktualizuj pip:
   ```bash
   pip install --upgrade pip --break-system-packages
   ```
4. Ponów instalację bibliotek

---

### Problem 4: Aplikacja zawiesza się lub działa wolno

**Rozwiązanie:**

1. Sprawdź obciążenie CPU: `htop`
2. Sprawdź temperaturę: `vcgencmd measure_temp`
3. Upewnij się, że Pi ma odpowiednie chłodzenie
4. Zmniejsz `SDR_SAMPLE_RATE` w kodzie na `0.256e6`
5. Zamknij inne aplikacje

---

### Problem 5: "Device or resource busy"

**Rozwiązanie:**

1. Zamknij wszystkie programy SDR (SDR++, GQRX, CubicSDR)
2. Odłącz i podłącz ponownie dongla
3. W ostateczności: `sudo reboot`

---

### Problem 6: Wersja V2 - Słyszę tylko ciszę (mimo włączonego skanowania)

**Rozwiązanie:**

1. **Sprawdź suwak Tłumika (Squelch)** - jeśli jest ustawiony wysoko, może wyciszać wszystkie sygnały
2. Ustaw Tłumik na **0** (całkowicie w lewo), aby wyłączyć funkcję
3. Stopniowo zwiększaj wartość, aż przestaniesz słyszeć szumy między stacjami

---

## Funkcje

### Wersja Podstawowa:
- ✅ Skanowanie pełnego pasma FM (87.5-108 MHz)
- ✅ Regulowana prędkość skanowania (50-500 ms na częstotliwość)
- ✅ Kontrola głośności w czasie rzeczywistym
- ✅ Demodulacja FM z automatyczną normalizacją audio
- ✅ Interfejs graficzny (Tkinter)
- ✅ System logowania zdarzeń
- ✅ Bezpieczne zatrzymywanie z czyszczeniem zasobów
- ✅ Wsparcie dla RTL-SDR v4

### Wersja Zaawansowana (V2) - wszystko powyżej plus:
- ✅ **Tłumik (Squelch)** - inteligentne wyciszanie słabych sygnałów
- ✅ **Tryb Mix (Losowy)** - skanowanie w losowej kolejności
- ✅ Lepsza kontrola nad jakością dźwięku

---

## Konfiguracja

Możesz dostosować parametry w plikach `ghostbox_fm.py` lub `ghostbox_fm_V2.py`:

```python
# Zakres częstotliwości FM
FM_START_FREQ = 87.5e6
FM_END_FREQ = 108.0e6
FM_STEP = 0.1e6  # Krok skanowania

# Parametry SDR
SDR_SAMPLE_RATE = 1.024e6  # Częstotliwość próbkowania SDR
SDR_GAIN = 'auto'  # lub wartość liczbowa np. 30

# Parametry audio
AUDIO_SAMPLE_RATE = 48000  # Częstotliwość próbkowania audio
```

---

## Wymagane biblioteki

### Python
- `tkinter` - interfejs graficzny (wbudowany w Pythona)
- `pyrtlsdr` - interfejs RTL-SDR
- `sounddevice` - odtwarzanie audio
- `numpy` - obliczenia numeryczne
- `scipy` - przetwarzanie sygnałów

### Systemowe
- `librtlsdr` - sterowniki RTL-SDR v4
- `libportaudio2` - biblioteka audio
- `libusb-1.0-0` - komunikacja USB

---

## Licencja

**Open Source** - Ten projekt jest wolnym oprogramowaniem. Każdy może go używać, modyfikować i dystrybuować bez ograniczeń. Kod jest udostępniony publicznie w celach edukacyjnych i społecznościowych.

---

## Współpraca

Zgłoszenia błędów, sugestie i pull requesty są mile widziane! Projekt jest otwarty dla wszystkich, którzy chcą pomóc w jego rozwoju.

---

## Zastrzeżenia

- Aplikacja jest przeznaczona do celów edukacyjnych i eksperymentalnych
- Przestrzegaj lokalnych przepisów dotyczących używania urządzeń radiowych
- Nie słuchaj nielegalnie transmisji radiowych
- Autor nie ponosi odpowiedzialności za niewłaściwe użycie aplikacji

---

## Kontakt

W razie pytań lub problemów otwórz Issue na GitHubie.

🔗 **Więcej informacji o RTL-SDR**: [https://www.rtl-sdr.com](https://www.rtl-sdr.com)

---

**Zbudowano z ❤️ dla społeczności Raspberry Pi i SDR**
