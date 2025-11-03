# Ghost Box Pi - Skaner Radiowy (FM/AM/AIR)

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi%205-red.svg)
![License](https://img.shields.io/badge/License-Open%20Source-green.svg)

Aplikacja do skanowania pasm radiowych (FM, AM, AIR, CB i więcej) wykorzystująca RTL-SDR v4 na Raspberry Pi. Ghost Box Pi umożliwia automatyczne przełączanie między stacjami radiowymi z regulowaną prędkością, głośnością i zaawansowaną kontrolą 
## Wymagania sprzętowe

- **Raspberry Pi 5** (zalecane) lub Raspberry Pi 4
- **RTL-SDR v4** (dongle USB) - **TYLKO ORYGINAŁ!** ⚠️
- **Oficjalny zasilacz** Raspberry Pi 5 (5V/5A USB-C)
- Głośnik/słuchawki (HDMI, Jack 3.5mm lub Bluetooth)
- Port USB 3.0 (niebieski) - zalecany dla RTL-SDR

### ⚠️ Gdzie kupić oryginalny RTL-SDR v4?

**BARDZO WAŻNE**: Na rynku jest wiele podróbek RTL-SDR, które mogą nie działać!

**Oficjalne sklepy:**

- 🔗 **Lista autoryzowanych sprzedawców**: <https://www.rtl-sdr.com/buy-rtl-sdr-dvb-t-dongles/>

**Jak rozpoznać oryginał RTL-SDR Blog v4:**

- ✅ Metalowa obudowa (niebieska lub srebrna)
- ✅ Logo “RTL-SDR Blog” na obudowie
- ✅ Złącze SMA (antena przykręcana)
- ✅ Cena około $35-45 USD (ok. 140-180 PLN)

**Oznaki podróbki:**

- ❌ Brak logo “RTL-SDR Blog”
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

-----

## Instalacja

### Krok 1: Aktualizacja systemu

Otwórz terminal i wykonaj następujące komendy:

```bash
sudo apt update
sudo apt upgrade -y
```

-----

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
sudo apt-get install libusb-1.0-0-dev git cmake pkg-config build-essential
```

**Pobierz kod źródłowy:**
```bash
git clone https://github.com/rtlsdrblog/rtl-sdr-blog
cd rtl-sdr-blog/
```

**Przygotuj i skompiluj:**
```bash
mkdir build
cd build
cmake ../ -DINSTALL_UDEV_RULES=ON
make
```

**Zainstaluj sterowniki:**
```bash
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

-----

### Krok 3: Sprawdzenie instalacji

Po restarcie podłącz RTL-SDR v4 do portu USB i wykonaj test:

```bash
rtl_test -t
```

**Oczekiwany wynik**: Powinieneś zobaczyć informacje o urządzeniu (np. “RTL-SDR Blog V4”) i test zakończony pomyślnie.

-----

### Krok 4: Instalacja Pythona i PIP

```bash
sudo apt install -y python3-pip
```

-----

### Krok 5: Instalacja zależności audio

```bash
sudo apt install -y libportaudio2 portaudio19-dev
```

-----

### Krok 6: Instalacja bibliotek Pythona

Wybierz zestaw bibliotek w zależności od wersji, którą chcesz uruchomić.

#### A) Dla Wersji Podstawowej (v1) oraz Zaawansowanej (v2):

```bash
pip install pyrtlsdr sounddevice numpy scipy --break-system-packages
```

#### B) Dla Wersji PRO (v4):

Ta komenda instaluje wszystko, czego potrzebujesz: customtkinter dla UI i soundfile do nagrywania.

```bash
pip install pyrtlsdr sounddevice numpy scipy customtkinter soundfile --break-system-packages
```

**Instalowane biblioteki:**

- `pyrtlsdr` - komunikacja z RTL-SDR
- `sounddevice` - odtwarzanie audio
- `numpy` - operacje numeryczne
- `scipy` - przetwarzanie sygnałów
- `customtkinter` - **(TYLKO DLA V4)** nowoczesny interfejs graficzny
- `soundfile` - **(TYLKO DLA V4)** zapisywanie plików audio .wav

-----

### Krok 7: Pobranie aplikacji

```bash
# Wróć do katalogu domowego
cd ~

# Sklonuj repozytorium
git clone https://github.com/gazda12345kamil-dotcom/ghost-box-pi.git
cd ghost-box-pi
```

Lub pobierz kod ręcznie i zapisz jako `ghostbox_fm.py` (podstawowa), `ghostbox_fm_V2.py` (zaawansowana) lub `ghostbox_pi_PRO_v4.py` (PRO) na pulpicie.

-----

## Uruchomienie

### Wersja Podstawowa:

```bash
python3 ghostbox_fm.py
```

### Wersja Zaawansowana (V2):

```bash
python3 ghostbox_fm_V2.py
```

### Wersja PRO (v4):

```bash
python3 ghostbox_pi_PRO_v4.py
```

-----
## Rozwiązywanie problemów

### Problem 1: RTL-SDR nie jest wykrywany

**Rozwiązanie:**

1. Sprawdź połączenie USB - użyj portu USB 3.0 (niebieskiego)
1. Weryfikuj w systemie: `lsusb` - szukaj ID `0bda:2838`
1. Sprawdź zasilanie - używaj oficjalnego zasilacza 5V/5A
1. Sprawdź czy masz oryginał: <https://www.rtl-sdr.com/buy-rtl-sdr-dvb-t-dongles/>
1. Odłącz i podłącz ponownie dongla
1. Sprawdź blacklist: `cat /etc/modprobe.d/blacklist-rtl-sdr.conf`

-----

### Problem 2: Brak dźwięku

**Rozwiązanie:**

1. **Wybierz wyjście audio:**

- Kliknij prawym przyciskiem ikonę głośnika na pasku zadań
- Wybierz odpowiednie urządzenie (HDMI, Headphones, Bluetooth)

1. **Sprawdź głośność systemową:**

- Kliknij lewym przyciskiem ikonę głośnika
- Upewnij się, że głośność nie jest wyciszona

1. **Test sounddevice:**
   
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

-----

### Problem 3: Błędy podczas instalacji bibliotek

**Rozwiązanie:**

1. Upewnij się, że zainstalowano wszystkie zależności systemowe (Krok 2 i 5)
1. Sprawdź połączenie internetowe
1. Zaktualizuj pip:
   
   ```bash
   pip install --upgrade pip --break-system-packages
   ```
1. Ponów instalację bibliotek (Krok 6)

-----

### Problem 4: “Device or resource busy”

**Rozwiązanie:**

1. Zamknij wszystkie programy SDR (SDR++, GQRX, CubicSDR)
1. Odłącz i podłącz ponownie dongla
1. W ostateczności: `sudo reboot`

-----

### Problem 5: Wersja V2/V4 - Słyszę tylko ciszę

**Rozwiązanie:**

1. **Sprawdź suwak Tłumika (Squelch)** - jeśli jest ustawiony wysoko, może wyciszać wszystkie sygnały
1. Ustaw Tłumik na **0** (całkowicie w lewo), aby wyłączyć funkcję
1. Stopniowo zwiększaj wartość, aż przestaniesz słyszeć szumy między stacjami

-----

### Problem 6: Błąd przy starcie V4: “No module named ‘customtkinter’”

**Rozwiązanie:**

Nie zainstalowałeś biblioteki interfejsu. Wykonaj polecenie:

```bash
pip install customtkinter --break-system-packages
```

-----

### Problem 7: Błąd przy starcie V4: “No module named ‘soundfile’”

**Rozwiązanie:**

Nie zainstalowałeś biblioteki do nagrywania audio. Wykonaj polecenie:

```bash
pip install soundfile --break-system-packages
```

-----

## Funkcje

### Wersja Podstawowa:

- ✅ Skanowanie pełnego pasma FM (87.5-108 MHz)
- ✅ Regulowana prędkość skanowania (50-500 ms)
- ✅ Kontrola głośności w czasie rzeczywistym
- ✅ Demodulacja FM z automatyczną normalizacją audio
- ✅ Interfejs graficzny (Tkinter)
- ✅ System logowania zdarzeń

### Wersja Zaawansowana (V2) - wszystko powyżej plus:

- ✅ **Tłumik (Squelch)** - wyciszanie szumów na FM
- ✅ **Tryb Mix (Losowy)** - skanowanie FM w losowej kolejności
- ✅ Lepsza kontrola nad jakością dźwięku

### Wersja PRO (v4) - wszystkie funkcje V2 plus:

- ✅ **Nowoczesny Interfejs** (CustomTkinter)
- ✅ **Skanowanie Wielu Pasm** (WBFM, AM, NBFM)
- ✅ **Pełne Miksowanie Pasm** (wybór checkboxami)
- ✅ **Zaawansowane Filtrowanie DSP** dla każdego trybu
- ✅ **Precyzyjny Tłumik (Squelch)** oparty na mocy sygnału
- ✅ **Nagrywanie sesji audio (REC)** - zapis do plików .wav
- ✅ **Wskaźnik siły sygnału (S-Meter)** - wizualizacja mocy sygnału
- ✅ **Zapisywanie i wczytywanie ustawień** - automatyczne zapamiętywanie konfiguracji

-----

## Konfiguracja

### Konfiguracja Pasm

Parametry można dostosować bezpośrednio w plikach `.py`.

#### Wersje v1 i v2 (`ghostbox_fm.py`, `ghostbox_fm_V2.py`):

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

#### Wersja PRO v4 (`ghostbox_pi_PRO_v4.py`):

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

### Zapisane Ustawienia

Wersja PRO (v4) automatycznie tworzy plik `ghostbox_config.json` w tym samym folderze. Przechowuje on:

- Ostatnie pozycje suwaków (głośność, prędkość, squelch)
- Stan pól wyboru pasm
- Tryb losowy (Mix)

Aby zresetować ustawienia do wartości domyślnych, wystarczy usunąć plik `ghostbox_config.json`.

-----

## Wymagane biblioteki

### Python

- `tkinter` - **(dla v1, v2)** interfejs graficzny (wbudowany w Pythona)
- `pyrtlsdr` - interfejs RTL-SDR
- `sounddevice` - odtwarzanie audio
- `numpy` - obliczenia numeryczne
- `scipy` - przetwarzanie sygnałów
- `customtkinter` - **(dla v4)** nowoczesny interfejs graficzny
- `soundfile` - **(dla v4)** zapisywanie plików audio .wav

### Systemowe

- `librtlsdr` - sterowniki RTL-SDR v4
- `libportaudio2` - biblioteka audio
- `libusb-1.0-0` - komunikacja USB

-----

## Licencja

**Open Source** - Ten projekt jest wolnym oprogramowaniem. Każdy może go używać, modyfikować i dystrybuować bez ograniczeń. Kod jest udostępniony publicznie w celach edukacyjnych i społecznościowych.

-----

## Współpraca

Zgłoszenia błędów, sugestie i pull requesty są mile widziane! Projekt jest otwarty dla wszystkich, którzy chcą pomóc w jego rozwoju.

-----

## Zastrzeżenia

- Aplikacja jest przeznaczona do celów edukacyjnych i eksperymentalnych
- Przestrzegaj lokalnych przepisów dotyczących używania urządzeń radiowych
- Nie słuchaj nielegalnie transmisji radiowych
- Autor nie ponosi odpowiedzialności za niewłaściwe użycie aplikacji

-----

## Kontakt

W razie pytań lub problemów otwórz Issue na GitHubie.

🔗 **Więcej informacji o RTL-SDR**: <https://www.rtl-sdr.com>

-----

**Zbudowano z ❤️ dla społeczności Raspberry Pi i SDR**
