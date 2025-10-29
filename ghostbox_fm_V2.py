#!/usr/bin/env python3
# =============================================================================
# Ghost Box Pi - Wersja tylko FM (Poprawka Stop + Poprawka Prędkości)
# Wersja z Tłumikiem (Squelch) i Trybem Losowym (Mix)
# =============================================================================
import tkinter as tk
from tkinter import font, messagebox, scrolledtext
import threading
import time
import numpy as np
import sounddevice as sd
from rtlsdr import RtlSdr
from scipy import signal
import queue

# --- Konfiguracja ---
FM_START_FREQ = 87.5e6
FM_END_FREQ = 108.0e6
FM_STEP = 0.1e6

SDR_SAMPLE_RATE = 1.024e6
SDR_GAIN = 'auto'
AUDIO_SAMPLE_RATE = 48000

# --- Zmienne globalne ---
sdr = None
scan_thread = None
audio_stream = None
msg_queue = queue.Queue() # Jedna kolejka do komunikacji

# --- Klasa SpiritBoxFM ---
class SpiritBoxFM:
    def __init__(self, msg_queue):
        self.sdr = None
        self._looping = False # Flaga kontrolująca pętlę run
        self.msg_queue = msg_queue
        self.current_center_freq = FM_START_FREQ
        # Oblicz liczbę kroków dla trybu losowego
        self.num_fm_steps = int((FM_END_FREQ - FM_START_FREQ) / FM_STEP)

    @property
    def looping(self):
        return self._looping

    @property
    def current_freq(self):
        return self.current_center_freq

    def log(self, message):
        """Wysyła wiadomość do logów przez kolejkę."""
        try:
            self.msg_queue.put(f"[LOG] {message}", block=False) # Nie blokuj jeśli kolejka pełna
        except queue.Full:
            print("Kolejka logów pełna.") # Loguj do konsoli jeśli GUI nie nadąża

    def setup_sdr(self):
        """Konfiguruje urządzenie RTL-SDR."""
        try:
            self.sdr = RtlSdr()
            self.sdr.sample_rate = SDR_SAMPLE_RATE
            self.sdr.gain = SDR_GAIN
            self.sdr.center_freq = self.current_center_freq
            self.log(f"RTL-SDR: Fs={self.sdr.sample_rate/1e6:.3f} MHz, Gain={SDR_GAIN}")
            return True
        except ImportError:
             self.msg_queue.put("[ERROR] Brak biblioteki 'rtlsdr'. Zainstaluj: pip install pyrtlsdr --break-system-packages")
             return False
        except Exception as e:
            if 'No devices found' in str(e) or 'Device or resource busy' in str(e):
                 err_msg = f"Nie można otworzyć RTL-SDR:\n{e}\n\n• Sprawdź połączenie.\n• Zamknij inne programy SDR.\n• Odłącz/Podłącz USB."
            else:
                 err_msg = f"Błąd inicjalizacji RTL-SDR:\n{e}\n\nSprawdź sterowniki V4."
            self.msg_queue.put(f"[ERROR] {err_msg}")
            return False

    def close_sdr(self):
        """Bezpiecznie zamyka połączenie z RTL-SDR."""
        if self.sdr:
            try:
                self.sdr.close()
                self.sdr = None
                self.log("RTL-SDR zamknięty.")
            except Exception as e:
                self.log(f"Błąd zamykania SDR: {e}")

    def fm_demodulate(self, samples):
        """Demoduluje sygnał FM i resampling."""
        # x ma o 1 próbkę mniej niż 'samples'
        x = np.diff(np.unwrap(np.angle(samples)))
        num_samples_target = int(len(x) * AUDIO_SAMPLE_RATE / SDR_SAMPLE_RATE)
        if num_samples_target > 0:
            audio_resampled = signal.resample(x, num_samples_target)
        else:
            audio_resampled = np.array([])
        return audio_resampled.astype(np.float32)

    def run(self, get_hold_time_func, get_volume_func, get_squelch_level_func, get_random_mode_func): # Dodano nowe funkcje
        """Główna pętla skanowania."""
        global audio_stream # Używamy globalnego streamu audio

        if not self.setup_sdr():
            self.msg_queue.put(None) # Sygnał zakończenia/błędu
            return

        self._looping = True
        current_freq_iter = self.current_center_freq

        try:
            self.log(f"Audio: Otwieram strumień {AUDIO_SAMPLE_RATE} Hz")
            sd.default.device = sd.query_hostapis()[0]['default_output_device']
            self.log(f"Audio: Używam domyślnego wyjścia: {sd.query_devices(sd.default.device)['name']}")
            # Otwórz stream tylko raz
            audio_stream = sd.OutputStream(samplerate=AUDIO_SAMPLE_RATE, channels=1, dtype='float32')
            audio_stream.start()
            self.log("Audio: Strumień otwarty.")

            while self._looping: # Sprawdzaj flagę na początku każdej iteracji
                # --- Pobierz aktualne wartości z GUI ---
                hold_time_sec = get_hold_time_func() / 1000.0
                squelch_level_gui = get_squelch_level_func() # Wartość 0-100
                is_random_mode = get_random_mode_func() # True/False
                
                # Przeskaluj squelch (0-100) na próg amplitudy (0.0 - 0.2)
                # 0.2 to dość wysoki próg dla znormalizowanych próbek I/Q
                squelch_threshold = squelch_level_gui / 500.0

                # --- Logika wyboru częstotliwości (Mix / Sekwencyjna) ---
                if is_random_mode:
                    random_step = np.random.randint(0, self.num_fm_steps + 1)
                    current_freq_iter = FM_START_FREQ + (random_step * FM_STEP)
                else:
                    # Tryb sekwencyjny (logika przeniesiona z końca pętli)
                    current_freq_iter += FM_STEP
                    if current_freq_iter > FM_END_FREQ:
                        current_freq_iter = FM_START_FREQ
                
                # --- Ustaw częstotliwość ---
                try:
                    # Sprawdź flagę przed potencjalnie blokującą operacją
                    if not self._looping: break
                    if abs(self.sdr.center_freq - current_freq_iter) > 1000:
                        self.sdr.center_freq = current_freq_iter
                    self.current_center_freq = current_freq_iter
                    self.msg_queue.put(f"[FREQ] {self.current_center_freq/1e6:.1f}")
                except Exception as e:
                    self.log(f"Błąd ustawiania Freq {current_freq_iter/1e6} MHz: {e}")
                    time.sleep(0.1)
                    continue

                # --- Odczytaj próbki ---
                num_samples = int(hold_time_sec * self.sdr.sample_rate)
                num_samples = max(1024, (num_samples // 1024) * 1024)

                try:
                    # Sprawdź flagę przed potencjalnie blokującą operacją
                    if not self._looping: break
                    samples = self.sdr.read_samples(num_samples)
                except Exception as read_err:
                    self.log(f"Błąd odczytu próbek: {read_err}. Kończę wątek.")
                    self._looping = False # Zatrzymaj pętlę w razie błędu
                    break

                # --- NOWA LOGIKA SQUELCH (TŁUMIKA) ---
                # Oblicz średnią amplitudę sygnału I/Q
                mean_amplitude = np.mean(np.abs(samples))
                
                if mean_amplitude < squelch_threshold:
                    # Sygnał jest PONIŻEJ progu - generuj ciszę
                    # Oblicz docelową liczbę próbek audio (o 1 mniej niż próbek I/Q)
                    num_samples_target = int((len(samples) - 1) * AUDIO_SAMPLE_RATE / SDR_SAMPLE_RATE)
                    if num_samples_target < 0: num_samples_target = 0
                    audio_samples = np.zeros(num_samples_target, dtype=np.float32)
                else:
                    # Sygnał jest POWYŻEJ progu - demoduluj normalnie
                    audio_samples = self.fm_demodulate(samples)
                # --- KONIEC LOGIKI SQUELCH ---


                # --- Demoduluj i zastosuj głośność ---
                if audio_samples.size > 0 and self._looping:
                    volume_level = get_volume_func() / 100.0
                    max_val = np.max(np.abs(audio_samples))
                    
                    if max_val > 0.001:
                         # Normalizacja (podbicie) i głośność
                         audio_normalized = audio_samples / max_val * volume_level * 0.9
                    else:
                         # Cisza (z bloku squelch lub po prostu cichy sygnał)
                         audio_normalized = audio_samples

                    try:
                        # Sprawdź flagę przed potencjalnie blokującą operacją
                        if not self._looping: break
                        if audio_stream:
                            audio_stream.write(audio_normalized)
                        else:
                            self.log("Błąd: Strumień audio nie istnieje podczas zapisu.")
                            self._looping = False; break
                    except Exception as audio_err:
                        self.log(f"Błąd zapisu audio: {audio_err}")
                        time.sleep(0.05) # Daj szansę systemowi audio

                # (Logika inkrementacji częstotliwości została przeniesiona na początek pętli)

        except ImportError:
             self.msg_queue.put("[ERROR] Brak 'sounddevice'/'numpy'. Zainstaluj je.")
        except Exception as e:
             self.msg_queue.put(f"[ERROR] Błąd w wątku: {e}")
        finally:
            self.log("Kończę wątek, sprzątam...")
            # Zamknij strumień audio globalny
            if audio_stream:
                try: audio_stream.stop(); audio_stream.close(); self.log("Audio: Strumień zamknięty.")
                except Exception as e: self.log(f"Błąd zamykania audio: {e}")
            audio_stream = None # Wyzeruj globalną zmienną
            self.close_sdr()
            self._looping = False # Upewnij się, że flaga jest False
            self.msg_queue.put(None) # Sygnał zakończenia
            self.log("Wątek zakończony.")

    def stop(self):
        """Sygnalizuje pętli skanowania, aby się zatrzymała."""
        self.log("Otrzymano sygnał stop.")
        self._looping = False # Ustaw flagę, pętla 'run' ją sprawdzi

    def close(self):
        """Zatrzymuje pętlę."""
        self.stop()


# --- Funkcje GUI ---
sb = SpiritBoxFM(msg_queue)
scan_thread_gui = None

def get_current_volume():
    """Zwraca aktualną wartość suwaka głośności."""
    try:
        # Odczytaj wartość tylko jeśli okno istnieje
        if window.winfo_exists():
            return volume_slider.get()
        else:
            return 50
    except tk.TclError:
        return 50

def get_current_hold_time():
    """Zwraca aktualną wartość suwaka prędkości."""
    try:
        if window.winfo_exists():
             return speed_slider.get()
        else:
             return 100 # Wartość domyślna
    except tk.TclError:
         return 100

def get_squelch_level():
    """Zwraca aktualną wartość suwaka tłumika."""
    try:
        if window.winfo_exists():
            return squelch_slider.get()
        else:
            return 10 # Wartość domyślna (niski squelch)
    except tk.TclError:
        return 10

def get_random_mode_state():
    """Zwraca stan checkboxa 'Mix'."""
    try:
        if window.winfo_exists():
            return random_mode_var.get()
        else:
            return False # Wartość domyślna
    except tk.TclError:
        return False


def start_scan_gui():
    """Uruchamia skanowanie."""
    global scan_thread_gui, sb
    
    if sb.looping: return
    if scan_thread_gui and scan_thread_gui.is_alive():
        log_message_gui("Czekam na zatrzymanie poprzedniego skanowania...")
        return
        
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    log_message_gui("Uruchamianie skanowania...")
    update_status("Skanowanie...")
    
    # Przekaż WSZYSTKIE funkcje do pobierania wartości z GUI
    scan_thread_gui = threading.Thread(target=sb.run, args=(
        get_current_hold_time, 
        get_current_volume, 
        get_squelch_level, 
        get_random_mode_state
    ), daemon=True)
    scan_thread_gui.start()
    window.after(100, check_msg_queue)

def stop_scan_gui():
    """Wysyła sygnał stop."""
    global sb
    if not sb.looping: return
    
    sb.stop() # Wyślij sygnał stop, wątek sam posprząta
    stop_button.config(state=tk.DISABLED) 
    update_status("Zatrzymywanie...")
    log_message_gui("Wysyłanie sygnału zatrzymania...")

def check_msg_queue():
    """Sprawdza kolejkę komunikatów z wątku."""
    global scan_thread_gui
    try:
        while True: # Przetwórz wszystkie wiadomości z kolejki
            message = msg_queue.get_nowait()
            
            if message is None: # Sygnał zakończenia wątku
                # Sprawdź czy wątek faktycznie się zakończył (na wszelki wypadek)
                if scan_thread_gui and not scan_thread_gui.is_alive():
                    update_gui_after_stop()
                else: # Jeśli None przyszło, a wątek żyje (dziwne), sprawdź później
                     window.after(200, check_msg_queue)
                return # Zakończ sprawdzanie w tej iteracji
            elif message.startswith("[FREQ]"):
                freq_str = message.split(" ")[1]
                update_freq_label(f"{freq_str} MHz")
            elif message.startswith("[LOG]") or message.startswith("[ERROR]"):
                log_message_gui(message.split(" ", 1)[1])
                # Jeśli to był błąd krytyczny z SDR, zaktualizuj GUI
                if "[ERROR] Nie można otworzyć RTL-SDR" in message or "[ERROR] Błąd inicjalizacji RTL-SDR" in message:
                     update_gui_after_stop()
                     return # Zakończ sprawdzanie
            else:
                log_message_gui(str(message))

    except queue.Empty:
        # Kolejka pusta, sprawdź ponownie później, jeśli wątek nadal działa
        # Sprawdzamy czy wątek żyje, a nie tylko flagę sb.looping
        if scan_thread_gui and scan_thread_gui.is_alive():
            window.after(100, check_msg_queue)
        else:
             # Wątek się zakończył, ale nie dostaliśmy None - zaktualizuj GUI
             # To się zdarza, jeśli np. był błąd przy starcie wątku
             if start_button['state'] == tk.DISABLED: # Jeśli GUI myśli, że skanuje
                  update_gui_after_stop()

    except Exception as e:
         print(f"Błąd w check_msg_queue: {e}")
         # Spróbuj kontynuować sprawdzanie
         if scan_thread_gui and scan_thread_gui.is_alive():
            window.after(100, check_msg_queue)


def update_gui_after_stop():
    """Aktualizuje GUI po zatrzymaniu skanowania."""
    # Upewnij się, że okno nadal istnieje
    if not window.winfo_exists():
        return
    update_status("Zatrzymano")
    freq_label.config(text="---.--- MHz")
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    log_message_gui("Skanowanie zatrzymane.")

def log_message_gui(message):
    """Dodaje wiadomość do widżetu logów."""
    try:
        if window.winfo_exists():
            log_text.config(state=tk.NORMAL)
            timestamp = time.strftime("[%H:%M:%S] ")
            log_text.insert(tk.END, timestamp + message + "\n")
            log_text.see(tk.END)
            log_text.config(state=tk.DISABLED)
    except tk.TclError:
        pass

# Pozostałe funkcje GUI (update_freq_label, update_status, etc.) bez zmian...

def update_freq_label(text):
    try:
        if window.winfo_exists(): freq_label.config(text=text)
    except tk.TclError: pass

def update_status(text):
    try:
        if window.winfo_exists():
            if "Skanowanie" in text: color = "#00FF00"
            elif "Gotowy" in text: color = "#FFFFFF"
            else: color = "red"
            status_label.config(text=f"Status: {text}", fg=color)
    except tk.TclError: pass

def update_speed_label(value):
    try:
        if window.winfo_exists(): speed_value_label.config(text=f"{value} ms")
    except tk.TclError: pass


def on_closing():
    """Obsługa zamykania aplikacji."""
    global sb, scan_thread_gui
    
    log_message_gui("Zamykanie aplikacji...")
    if sb.looping:
        sb.stop() # Wyślij sygnał stop
        log_message_gui("Wysłano stop do wątku, czekam na zakończenie...")
        # Poczekaj krótko na wątek, ale nie blokuj zamknięcia na długo
        if scan_thread_gui and scan_thread_gui.is_alive():
             scan_thread_gui.join(timeout=0.5) 
             if scan_thread_gui.is_alive():
                  print("Wątek nie zakończył się w czasie, zamykam GUI.")
                  # Awaryjne zamknięcie SDR, jeśli wątek utknął
                  sb.close_sdr() 
    else:
         sb.close_sdr() 
    
    window.destroy()
    print("Okno GUI zamknięte.")

def show_help():
    help_text = """Ghost Box Pi - Wersja FM (pyrtlsdr)

PASMO: FM (87.5-108 MHz)

KONTROLA:
• Prędkość: Czas na częstotliwość (ms).
• Głośność: Poziom głośności wyjściowej.
• Tłumik (Squelch): Próg siły sygnału. Wycisza sygnały poniżej progu. Ustaw na 0, aby wyłączyć.
• Mix (Losowo): Skanuje losowe częstotliwości zamiast po kolei.

WYMAGANIA:
• RTL-SDR V4, Sterowniki V4
• Biblioteki: pyrtlsdr, sounddevice, numpy, scipy
• PulseAudio
"""
    messagebox.showinfo("Pomoc - Ghost Box Pi (FM)", help_text)

# --- Tworzenie okna interfejsu (z logami i głośnością) ---

window = tk.Tk()
window.title("Ghost Box Pi - FM (vFinal+Mix+Squelch)")
# Zwiększamy wysokość okna, aby zmieścić nowe kontrolki
window.geometry("480x480") 
window.configure(bg='black')
window.protocol("WM_DELETE_WINDOW", on_closing)

# --- Zmienne globalne GUI ---
random_mode_var = tk.BooleanVar(value=False)

# Czcionki
title_font = font.Font(family='Courier', size=24, weight='bold')
label_font = font.Font(family='Courier', size=12, weight='bold')
status_font = font.Font(family='Courier', size=11)
value_font = font.Font(family='Courier', size=14, weight='bold')
log_font = font.Font(family='Consolas', size=8)

# === Interfejs użytkownika ===

freq_label = tk.Label(window, text="---.--- MHz", font=title_font, fg='cyan', bg='black')
freq_label.pack(pady=10)

sliders_frame = tk.Frame(window, bg='black')
sliders_frame.pack(pady=5, fill=tk.X, padx=10)

speed_frame = tk.Frame(sliders_frame, bg='black')
speed_slider = tk.Scale(speed_frame, from_=50, to=500, resolution=10, orient=tk.HORIZONTAL, label="Prędkość", fg='white', bg='black', highlightbackground='black', troughcolor='gray20', length=200, showvalue=0, command=update_speed_label)
speed_slider.set(100) 
speed_slider.pack(side=tk.LEFT)
speed_value_label = tk.Label(speed_frame, text="100 ms", font=value_font, fg='yellow', bg='black', width=6)
speed_value_label.pack(side=tk.LEFT, padx=5)
speed_frame.pack(side=tk.LEFT, padx=5)

volume_frame = tk.Frame(sliders_frame, bg='black')
volume_slider = tk.Scale(volume_frame, from_=0, to=100, resolution=1, orient=tk.HORIZONTAL, label="Głośność", fg='white', bg='black', highlightbackground='black', troughcolor='gray20', length=150)
volume_slider.set(80)
volume_slider.pack(side=tk.LEFT)
volume_frame.pack(side=tk.RIGHT, padx=5)

# --- NOWA KONTROLKA: Squelch (Tłumik) ---
squelch_frame = tk.Frame(window, bg='black')
squelch_frame.pack(pady=5, fill=tk.X, padx=10)

squelch_slider = tk.Scale(squelch_frame, from_=0, to=100, resolution=1, orient=tk.HORIZONTAL, label="Tłumik (Squelch)", fg='white', bg='black', highlightbackground='black', troughcolor='gray20', length=400)
squelch_slider.set(10) # Domyślnie niski próg
squelch_slider.pack(padx=10)


controls_frame = tk.Frame(window, bg='black')
controls_frame.pack(pady=10)

start_button = tk.Button(controls_frame, text="START", command=start_scan_gui, font=label_font, bg='green', fg='white', width=8, height=1, state=tk.NORMAL)
start_button.pack(side=tk.LEFT, padx=10)

stop_button = tk.Button(controls_frame, text="STOP", command=stop_scan_gui, font=label_font, bg='red', fg='white', width=8, height=1, state=tk.DISABLED)
stop_button.pack(side=tk.LEFT, padx=10)

# --- NOWA KONTROLKA: Tryb Losowy (Mix) ---
random_mode_check = tk.Checkbutton(controls_frame, text="Mix (Losowo)", variable=random_mode_var, font=label_font, fg='yellow', bg='black', selectcolor='gray20', activebackground='black', activeforeground='yellow', borderwidth=0, highlightthickness=0)
random_mode_check.pack(side=tk.LEFT, padx=10)


log_label = tk.Label(window, text="Log:", font=status_font, fg='white', bg='black')
log_label.pack(pady=(5,0))
log_text = scrolledtext.ScrolledText(window, height=6, bg='gray10', fg='cyan', font=log_font, state=tk.DISABLED, wrap=tk.WORD)
log_text.pack(pady=5, padx=10, fill=tk.X)


help_button = tk.Button(window, text="?", command=show_help, font=('Courier', 10, 'bold'), bg='gray20', fg='white', width=2, height=1)
help_button.place(x=450, y=5)

status_label = tk.Label(window, text="Status: Inicjalizacja...", font=status_font, fg='#FFFFFF', bg='black')
status_label.pack(side=tk.BOTTOM, pady=5)

# === Uruchomienie aplikacji ===
if __name__ == "__main__":
    try:
        import rtlsdr
        import sounddevice
        import numpy
        import scipy
        log_message_gui("Aplikacja uruchomiona. Sprawdzam zależności...")
        log_message_gui(f"Numpy: {np.__version__}, Scipy: {scipy.__version__}, SoundDevice: {sd.__version__}")
        status_label.config(text="Status: Gotowy")
        window.mainloop()
    except ImportError as e:
         missing_lib = str(e).split("'")[-2]
         messagebox.showerror("Brak Biblioteki", f"Nie znaleziono wymaganej biblioteki: '{missing_lib}'\n\nZainstaluj ją używając:\npip install {missing_lib} --break-system-packages")
         try: window.destroy() 
         except: pass
    except Exception as general_e:
        messagebox.showerror("Błąd Startowy", f"Wystąpił nieoczekiwany błąd podczas startu:\n{general_e}")
        try: window.destroy() 
        except: pass