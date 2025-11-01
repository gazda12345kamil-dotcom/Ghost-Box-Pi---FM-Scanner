#!/usr/bin/env python3
# =============================================================================
# Ghost Box Pi - Wersja PRO v4 (Multi-Band-Mix)
#
# POPRAWKA: Składnia (IndentationError) w funkcjach GUI
#
# Funkcje:
# - Nowoczesny UI (CustomTkinter)
# - Skanowanie wielopasmowe przez Checkboxy (wybierz co chcesz miksować)
# - Dodane pasma NBFM (WX, 2M-HAM)
# - Trzy oddzielne filtry i demodulatory (WBFM, AM, NBFM)
# - Mocny Squelch (oparty o moc po filtracji)
# =============================================================================
import customtkinter as ctk
from tkinter import messagebox
import threading
import time
import numpy as np
import sounddevice as sd
from rtlsdr import RtlSdr
from scipy import signal
import queue

# --- Konfiguracja ---

# 1. Definicje Pasm (WBFM, AM, NBFM)
BANDS_CONFIG = {
    "FM":      {'name': "FM",  'start': 87.5e6,  'end': 108.0e6, 'step': 0.1e6,  'mode': "WBFM"},
    "AIR":     {'name': "AIR", 'start': 108.1e6, 'end': 137.0e6, 'step': 0.025e6, 'mode': "AM"},
    "CB":      {'name': "CB",  'start': 26.965e6,'end': 27.405e6,'step': 0.01e6, 'mode': "AM"},
    # UWAGA: Pasmo "AM" wymaga upconvertera lub trybu Direct Sampling
    "AM":      {'name': "AM", 'start': 531e3,   'end': 1701e3,  'step': 9e3,    'mode': "AM"},
    "WX":      {'name': "WX",  'start': 162.400e6,'end': 162.550e6,'step': 0.025e6,'mode': "NBFM"},
    "2M-HAM":  {'name': "2M-HAM",'start': 144.0e6, 'end': 146.0e6, 'step': 0.025e6,'mode': "NBFM"}
}
# Lista kluczy do iteracji
ALL_BAND_NAMES = list(BANDS_CONFIG.keys())

# 2. Parametry SDR
SDR_SAMPLE_RATE = 1.024e6
SDR_GAIN = 'auto'

# 3. Parametry Audio
AUDIO_SAMPLE_RATE = 48000

# --- Zmienne globalne ---
sdr = None
scan_thread = None
audio_stream = None
msg_queue = queue.Queue()

# --- Klasa SpiritBox ---
class SpiritBoxMultiBand:
    def __init__(self, msg_queue):
        self.sdr = None
        self._looping = False
        self.msg_queue = msg_queue
        self.current_center_freq = BANDS_CONFIG["FM"]['start']
        self.current_band_mode = "WBFM"

        # Zmienne stanu dla skanowania sekwencyjnego
        self.current_seq_band_idx = 0 # Indeks na liście *aktywnych* pasm
        self.current_seq_freqs = {} # Słownik przechowujący ostatnią freq dla każdego pasma

        # --- Tworzenie filtrów DSP (jeden raz) ---
        self.log("Tworzenie filtrów DSP...")

        # WBFM (Radio FM): LPF 100kHz, decymacja x4 -> Fs = 256k
        self.wbfm_taps = signal.firwin(101, 100e3 / (SDR_SAMPLE_RATE / 2), window='hamming')
        self.wbfm_decimation = 4
        self.wbfm_fs_new = SDR_SAMPLE_RATE / self.wbfm_decimation
        self.log(f"Filtr WBFM: Fs_out={self.wbfm_fs_new/1e3}k")

        # AM (AIR, CB, AM): LPF 5kHz, decymacja x20 -> Fs = 51.2k
        self.am_taps = signal.firwin(101, 5e3 / (SDR_SAMPLE_RATE / 2), window='hamming')
        self.am_decimation = 20
        self.am_fs_new = SDR_SAMPLE_RATE / self.am_decimation
        self.log(f"Filtr AM: Fs_out={self.am_fs_new/1e3}k")
        
        # NBFM (WX, HAM): LPF 8kHz, decymacja x50 -> Fs = 20.48k
        self.nbfm_taps = signal.firwin(101, 8e3 / (SDR_SAMPLE_RATE / 2), window='hamming')
        self.nbfm_decimation = 50
        self.nbfm_fs_new = SDR_SAMPLE_RATE / self.nbfm_decimation
        self.log(f"Filtr NBFM: Fs_out={self.nbfm_fs_new/1e3}k")


    @property
    def looping(self): return self._looping

    def log(self, message):
        try: self.msg_queue.put(f"[LOG] {message}", block=False)
        except queue.Full: print("Kolejka logów pełna.")

    def setup_sdr(self):
        try:
            self.sdr = RtlSdr()
            self.sdr.sample_rate = SDR_SAMPLE_RATE
            self.sdr.gain = SDR_GAIN
            self.sdr.center_freq = self.current_center_freq
            self.log(f"RTL-SDR: Fs={self.sdr.sample_rate/1e6:.3f} MHz, Gain={SDR_GAIN}")
            return True
        except Exception as e:
            err_msg = f"Nie można otworzyć RTL-SDR:\n{e}\n\nSprawdź sterowniki V4, połączenie USB i zamknij inne programy SDR."
            self.msg_queue.put(f"[ERROR] {err_msg}")
            return False

    def close_sdr(self):
        if self.sdr:
            try: self.sdr.close(); self.sdr = None; self.log("RTL-SDR zamknięty.")
            except Exception as e: self.log(f"Błąd zamykania SDR: {e}")

    # === Demodulatory ===
    def fm_demodulate(self, samples, fs_in):
        """Demoduluje WBFM lub NBFM (różni się tylko filtrem wejściowym)."""
        x = np.diff(np.unwrap(np.angle(samples)))
        num_samples_target = int(len(x) * AUDIO_SAMPLE_RATE / fs_in)
        if num_samples_target > 0:
            return signal.resample(x, num_samples_target).astype(np.float32)
        return np.array([], dtype=np.float32)

    def am_demodulate(self, samples, fs_in):
        """Demoduluje AM."""
        audio_envelope = np.abs(samples)
        b, a = signal.butter(1, 100.0, 'high', fs=fs_in)
        audio_filtered = signal.lfilter(b, a, audio_envelope)
        num_samples_target = int(len(audio_filtered) * AUDIO_SAMPLE_RATE / fs_in)
        if num_samples_target > 0:
            return signal.resample(audio_filtered, num_samples_target).astype(np.float32)
        return np.array([], dtype=np.float32)

    # === ZMODYFIKOWANA PĘTLA 'run' ===
    def run(self, get_hold_time_func, get_volume_func, get_squelch_level_func, get_random_mode_func, get_active_bands_func):
        """Główna pętla skanowania."""
        global audio_stream

        if not self.setup_sdr():
            self.msg_queue.put(None); return

        self._looping = True

        try:
            self.log(f"Audio: Otwieram strumień {AUDIO_SAMPLE_RATE} Hz")
            sd.default.device = sd.query_hostapis()[0]['default_output_device']
            self.log(f"Audio: Używam wyjścia: {sd.query_devices(sd.default.device)['name']}")
            audio_stream = sd.OutputStream(samplerate=AUDIO_SAMPLE_RATE, channels=1, dtype='float32')
            audio_stream.start()
            self.log("Audio: Strumień otwarty.")

            while self._looping:
                # --- 1. Pobierz wartości z GUI ---
                hold_time_sec = get_hold_time_func() / 1000.0
                squelch_level_gui = get_squelch_level_func() # 0-100
                is_random_mode = get_random_mode_func() # True/False
                active_bands = get_active_bands_func() # Lista nazw, np. ["FM", "AIR"]
                
                if not active_bands: # Jeśli nic nie jest zaznaczone
                    time.sleep(0.2)
                    continue
                
                # --- 2. Logika wyboru częstotliwości ---
                current_freq_iter = 0
                band_to_scan = None
                
                if is_random_mode:
                    # Tryb losowy: wylosuj pasmo z aktywnych, potem wylosuj krok
                    random_band_key = np.random.choice(active_bands)
                    band_to_scan = BANDS_CONFIG[random_band_key]
                    num_steps = int((band_to_scan['end'] - band_to_scan['start']) / band_to_scan['step'])
                    random_step = np.random.randint(0, num_steps + 1)
                    current_freq_iter = band_to_scan['start'] + (random_step * band_to_scan['step'])
                
                else:
                    # Tryb sekwencyjny: iteruj po aktywnych pasmach
                    # Upewnij się, że indeks jest w zakresie aktywnych pasm
                    if self.current_seq_band_idx >= len(active_bands):
                        self.current_seq_band_idx = 0
                        
                    band_key = active_bands[self.current_seq_band_idx]
                    band_to_scan = BANDS_CONFIG[band_key]
                    
                    # Pobierz lub zainicjuj częstotliwość dla tego pasma
                    if band_key not in self.current_seq_freqs:
                        self.current_seq_freqs[band_key] = band_to_scan['start']
                    
                    current_freq_iter = self.current_seq_freqs[band_key]
                    
                    # Inkrementacja na następną pętlę
                    self.current_seq_freqs[band_key] += band_to_scan['step']
                    if self.current_seq_freqs[band_key] > band_to_scan['end']:
                        self.current_seq_freqs[band_key] = band_to_scan['start'] # Zresetuj freq tego pasma
                        self.current_seq_band_idx = (self.current_seq_band_idx + 1) % len(active_bands) # Przejdź do nast. pasma

                
                # --- 3. Ustaw częstotliwość ---
                self.current_band_mode = band_to_scan['mode']
                try:
                    if not self._looping: break
                    
                    # Logika Direct Sampling (opcjonalna, wymaga testów)
                    # is_low_freq = current_freq_iter < 24e6
                    # if is_low_freq and self.sdr.get_direct_sampling() != 1:
                    #     self.sdr.set_direct_sampling('q'); self.log("Włączono Direct Sampling")
                    # elif not is_low_freq and self.sdr.get_direct_sampling() != 0:
                    #     self.sdr.set_direct_sampling(0); self.log("Wyłączono Direct Sampling")

                    if abs(self.sdr.center_freq - current_freq_iter) > 1000:
                        self.sdr.center_freq = current_freq_iter
                        
                    self.current_center_freq = current_freq_iter
                    self.msg_queue.put(f"[FREQ] {self.current_center_freq/1e6:.3f}")
                    self.msg_queue.put(f"[MODE] {self.current_band_mode}")
                except Exception as e:
                    self.log(f"Błąd ustawiania Freq {current_freq_iter/1e6} MHz: {e}")
                    time.sleep(0.1); continue

                # --- 4. Odczytaj próbki ---
                num_samples = int(hold_time_sec * self.sdr.sample_rate)
                num_samples = max(2048, (num_samples // 1024) * 1024)
                try:
                    if not self._looping: break
                    samples = self.sdr.read_samples(num_samples)
                except Exception as read_err:
                    self.log(f"Błąd odczytu próbek: {read_err}."); self._looping = False; break
                
                # --- 5. DSP: Filtracja i Decymacja ---
                decimated_samples = None
                fs_new = 0
                if self.current_band_mode == "WBFM":
                    filtered_samples = signal.lfilter(self.wbfm_taps, 1.0, samples)
                    decimated_samples = filtered_samples[::self.wbfm_decimation]
                    fs_new = self.wbfm_fs_new
                elif self.current_band_mode == "AM":
                    filtered_samples = signal.lfilter(self.am_taps, 1.0, samples)
                    decimated_samples = filtered_samples[::self.am_decimation]
                    fs_new = self.am_fs_new
                elif self.current_band_mode == "NBFM":
                    filtered_samples = signal.lfilter(self.nbfm_taps, 1.0, samples)
                    decimated_samples = filtered_samples[::self.nbfm_decimation]
                    fs_new = self.nbfm_fs_new
                if decimated_samples is None or decimated_samples.size == 0: continue

                # --- 6. SQUELCH (na mocy po filtracji) ---
                mean_power = np.mean(np.abs(decimated_samples) ** 2)
                log_min, log_max = -8.0, -3.0 # Próg logarytmiczny
                squelch_log_threshold = log_min + (squelch_level_gui / 100.0) * (log_max - log_min)
                squelch_threshold = 10 ** squelch_log_threshold
                
                audio_samples = None
                if mean_power < squelch_threshold and squelch_level_gui > 0:
                    num_samples_target = int(len(decimated_samples) * AUDIO_SAMPLE_RATE / fs_new)
                    audio_samples = np.zeros(max(0, num_samples_target), dtype=np.float32)
                else:
                    if self.current_band_mode == "WBFM" or self.current_band_mode == "NBFM":
                        audio_samples = self.fm_demodulate(decimated_samples, fs_new)
                    elif self.current_band_mode == "AM":
                        audio_samples = self.am_demodulate(decimated_samples, fs_new)
                
                # --- 7. Odtwarzanie Audio ---
                if audio_samples is not None and audio_samples.size > 0 and self._looping:
                    volume_level = get_volume_func() / 100.0
                    max_val = np.max(np.abs(audio_samples))
                    
                    if max_val > 0.001:
                         # Podbicie dla cichszych trybów AM i NBFM
                         gain = 1.5 if self.current_band_mode in ["AM", "NBFM"] else 0.9
                         audio_normalized = (audio_samples / max_val) * volume_level * gain
                    else:
                         audio_normalized = audio_samples # Cisza

                    try:
                        if not self._looping: break
                        if audio_stream: audio_stream.write(audio_normalized)
                    except Exception as audio_err:
                        self.log(f"Błąd zapisu audio: {audio_err}"); time.sleep(0.05)

        except Exception as e:
             self.msg_queue.put(f"[ERROR] Błąd krytyczny w wątku: {e}")
        finally:
            self.log("Kończę wątek, sprzątam...")
            if audio_stream:
                try: audio_stream.stop(); audio_stream.close(); self.log("Audio: Strumień zamknięty.")
                except Exception as e: self.log(f"Błąd zamykania audio: {e}")
            audio_stream = None
            self.close_sdr()
            self._looping = False
            self.msg_queue.put(None)
            self.log("Wątek zakończony.")

    def stop(self): self._looping = False
    def close(self): self.stop()


# --- Logika GUI (CustomTkinter) ---

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

sb = SpiritBoxMultiBand(msg_queue)
scan_thread_gui = None

# Zmienne dla widgetów
speed_slider = None
volume_slider = None
squelch_slider = None
random_mode_var = None
band_check_vars = {} # ZMIANA: Słownik na checkboxy
start_button = None
stop_button = None
freq_label = None
mode_label = None
status_label = None
log_text = None
window = None

# =================================================================
# === POPRAWIONE FUNKCJE 'get' (Naprawa SyntaxError) ===
# =================================================================
def get_current_volume():
    try: return volume_slider.get()
    except Exception: return 50

def get_current_hold_time():
    try: return speed_slider.get()
    except Exception: return 100

def get_squelch_level():
    try: return squelch_slider.get()
    except Exception: return 10

def get_random_mode_state():
    try: return random_mode_var.get()
    except Exception: return False

def get_active_bands(): # NOWA funkcja
    """Zwraca listę NAZW aktywnych pasm."""
    active = []
    try:
        if not window.winfo_exists(): return ["FM"]
        for band_name, var in band_check_vars.items():
            if var.get():
                active.append(band_name)
        return active
    except Exception:
        return ["FM"]
# =================================================================
# =================================================================


def start_scan_gui():
    global scan_thread_gui, sb
    if sb.looping: return
    if scan_thread_gui and scan_thread_gui.is_alive():
        log_message_gui("Czekam na zatrzymanie poprzedniego..."); return
        
    start_button.configure(state=ctk.DISABLED)
    stop_button.configure(state=ctk.NORMAL)
    log_message_gui("Uruchamianie skanowania...")
    update_status("Skanowanie...")
    
    # ZMIANA: Przekazanie get_active_bands
    scan_thread_gui = threading.Thread(target=sb.run, args=(
        get_current_hold_time, 
        get_current_volume, 
        get_squelch_level, 
        get_random_mode_state,
        get_active_bands # NOWA
    ), daemon=True)
    scan_thread_gui.start()
    window.after(100, check_msg_queue)

def stop_scan_gui():
    global sb
    if not sb.looping: return
    sb.stop()
    stop_button.configure(state=ctk.DISABLED) 
    update_status("Zatrzymywanie...")
    log_message_gui("Wysyłanie sygnału zatrzymania...")

def check_msg_queue():
    global scan_thread_gui
    try:
        while True:
            message = msg_queue.get_nowait()
            if message is None:
                if scan_thread_gui and not scan_thread_gui.is_alive(): update_gui_after_stop()
                else: window.after(200, check_msg_queue)
                return
            elif message.startswith("[FREQ]"): update_freq_label(f"{message.split(' ')[1]} MHz")
            elif message.startswith("[MODE]"): update_mode_label(f"Tryb: {message.split(' ')[1]}")
            elif message.startswith("[LOG]") or message.startswith("[ERROR]"):
                log_message_gui(message.split(" ", 1)[1])
                if "[ERROR] Nie można otworzyć RTL-SDR" in message:
                     update_gui_after_stop(); return
            else: log_message_gui(str(message))
    except queue.Empty:
        if scan_thread_gui and scan_thread_gui.is_alive():
            window.after(100, check_msg_queue)
        else:
             if start_button.cget('state') == ctk.DISABLED: update_gui_after_stop()
    except Exception: pass # Ignoruj błędy GUI podczas zamykania

# Funkcje aktualizujące GUI
def update_gui_after_stop():
    if not window.winfo_exists(): return
    update_status("Zatrzymano"); freq_label.configure(text="---.--- MHz")
    mode_label.configure(text="Tryb: -"); start_button.configure(state=ctk.NORMAL)
    stop_button.configure(state=ctk.DISABLED); log_message_gui("Skanowanie zatrzymane.")

def log_message_gui(message):
    try:
        if window.winfo_exists():
            log_text.configure(state=ctk.NORMAL)
            log_text.insert(ctk.END, f"{time.strftime('[%H:%M:%S] ')}{message}\n")
            log_text.see(ctk.END); log_text.configure(state=ctk.DISABLED)
    except Exception: pass

# =================================================================
# === POPRAWIONE FUNKCJE 'update' (Naprawa SyntaxError) ===
# =================================================================
def update_freq_label(text):
    try: freq_label.configure(text=text)
    except Exception: pass

def update_mode_label(text):
    try: mode_label.configure(text=text)
    except Exception: pass

def update_status(text):
    try:
        color = "#FFFFFF";
        if "Skanowanie" in text: color = "#00FF00"
        elif "Gotowy" in text: color = "#FFFFFF"
        else: color = "#FF5555"
        status_label.configure(text=f"Status: {text}", text_color=color)
    except Exception: pass

def update_speed_label(value):
    try: speed_label.configure(text=f"Prędkość: {int(value)} ms")
    except Exception: pass

def update_volume_label(value):
    try: volume_label.configure(text=f"Głośność: {int(value)} %")
    except Exception: pass

def update_squelch_label(value):
    try: squelch_label.configure(text=f"Tłumik (Squelch): {int(value)}")
    except Exception: pass
# =================================================================
# =================================================================

def on_closing():
    global sb, scan_thread_gui
    log_message_gui("Zamykanie aplikacji...")
    if sb.looping:
        sb.stop()
        if scan_thread_gui and scan_thread_gui.is_alive():
             scan_thread_gui.join(timeout=0.5) 
    sb.close_sdr(); window.destroy(); print("Okno GUI zamknięte.")

def show_help():
    help_text = """Ghost Box Pi - Wersja PRO v4

TRYBY SKANOWANIA:
• Zaznacz pasma, które chcesz skanować (np. "FM" i "CB").
• Skanowanie Sekwencyjne: (odznaczony "Mix") Skanuje po kolei *tylko zaznaczone* pasma.
• Skanowanie Losowe: (zaznaczony "Mix") Losuje częstotliwości *tylko z zaznaczonych* pasm.

KONTROLA:
• Tłumik (Squelch): Wycisza słabe sygnały. 0 = wyłączony.

UWAGA: Pasmo "AM" wymaga specjalnego sprzętu (upconvertera) i prawdopodobnie nie zadziała bez niego.
"""
    messagebox.showinfo("Pomoc - Ghost Box Pi PRO v4", help_text)

# --- Tworzenie okna interfejsu (CustomTkinter) ---

window = ctk.CTk()
window.title("Ghost Box Pi - PRO v4 (Multi-Mix)")
window.geometry("500x660") # Trochę wyższe okno
window.protocol("WM_DELETE_WINDOW", on_closing)
window.grid_columnconfigure(0, weight=1)

# === Interfejs użytkownika ===

# --- 1. Wyświetlacz ---
display_frame = ctk.CTkFrame(window)
display_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
display_frame.grid_columnconfigure(0, weight=1)
freq_label = ctk.CTkLabel(display_frame, text="---.--- MHz", font=ctk.CTkFont(family='Courier', size=36, weight='bold'), text_color="#00FFFF")
freq_label.grid(row=0, column=0, pady=10)
mode_label = ctk.CTkLabel(display_frame, text="Tryb: -", font=ctk.CTkFont(family='Courier', size=16), text_color="#FFFFFF")
mode_label.grid(row=1, column=0, pady=(0, 10))

# --- 2. Wybór Pasm (ZMIANA: Checkboxy) ---
band_frame = ctk.CTkFrame(window)
band_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
band_frame.grid_columnconfigure((0, 1, 2), weight=1) # 3 kolumny

band_check_vars = {}
row_idx, col_idx = 0, 0
for band_name in ALL_BAND_NAMES:
    var = ctk.BooleanVar(value=(band_name=="FM")) # Domyślnie tylko FM
    check = ctk.CTkCheckBox(band_frame, text=band_name, variable=var, font=ctk.CTkFont(size=14, weight='bold'))
    check.grid(row=row_idx, column=col_idx, padx=10, pady=8, sticky="w")
    band_check_vars[band_name] = var
    
    col_idx += 1
    if col_idx > 2: # 3 kolumny
        col_idx = 0
        row_idx += 1

# --- 3. Suwaki (bez zmian) ---
sliders_frame = ctk.CTkFrame(window)
sliders_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
sliders_frame.grid_columnconfigure(0, weight=1)
sliders_frame.grid_columnconfigure(1, weight=1)
# Prędkość
speed_frame = ctk.CTkFrame(sliders_frame, fg_color="transparent")
speed_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
speed_frame.grid_columnconfigure(0, weight=1)
speed_label = ctk.CTkLabel(speed_frame, text="Prędkość: 100 ms", font=ctk.CTkFont(size=12))
speed_label.grid(row=0, column=0, sticky="w")
speed_slider = ctk.CTkSlider(speed_frame, from_=50, to=500, number_of_steps=45, command=update_speed_label)
speed_slider.set(100); speed_slider.grid(row=1, column=0, sticky="ew")
# Głośność
volume_frame = ctk.CTkFrame(sliders_frame, fg_color="transparent")
volume_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
volume_frame.grid_columnconfigure(0, weight=1)
volume_label = ctk.CTkLabel(volume_frame, text="Głośność: 80 %", font=ctk.CTkFont(size=12))
volume_label.grid(row=0, column=0, sticky="w")
volume_slider = ctk.CTkSlider(volume_frame, from_=0, to=100, number_of_steps=100, command=update_volume_label)
volume_slider.set(80); volume_slider.grid(row=1, column=0, sticky="ew")
# Squelch
squelch_frame = ctk.CTkFrame(window)
squelch_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
squelch_frame.grid_columnconfigure(0, weight=1)
squelch_label = ctk.CTkLabel(squelch_frame, text="Tłumik (Squelch): 10", font=ctk.CTkFont(size=12))
squelch_label.grid(row=0, column=0, sticky="w", padx=5)
squelch_slider = ctk.CTkSlider(squelch_frame, from_=0, to=100, number_of_steps=100, command=update_squelch_label)
squelch_slider.set(10); squelch_slider.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))


# --- 4. Kontrolki (ZMIANA: Usunięto 'Skan Wstecz') ---
controls_frame = ctk.CTkFrame(window, fg_color="transparent")
controls_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
controls_frame.grid_columnconfigure(0, weight=2) # START
controls_frame.grid_columnconfigure(1, weight=2) # STOP
controls_frame.grid_columnconfigure(2, weight=1) # Mix

start_button = ctk.CTkButton(controls_frame, text="START", command=start_scan_gui, font=ctk.CTkFont(size=14, weight='bold'), fg_color="#008800", hover_color="#00AA00", text_color_disabled="#999999")
start_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew", ipady=8)

stop_button = ctk.CTkButton(controls_frame, text="STOP", command=stop_scan_gui, font=ctk.CTkFont(size=14, weight='bold'), fg_color="#CC0000", hover_color="#FF0000", state=ctk.DISABLED, text_color_disabled="#999999")
stop_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew", ipady=8)

random_mode_var = ctk.BooleanVar(value=False)
random_mode_check = ctk.CTkCheckBox(controls_frame, text="Mix (Losowo)", variable=random_mode_var, font=ctk.CTkFont(size=14, weight='bold'))
random_mode_check.grid(row=0, column=2, padx=10, pady=5, sticky="w")

# --- 5. Logi ---
log_text = ctk.CTkTextbox(window, height=120, font=ctk.CTkFont(family='Consolas', size=11), state=ctk.DISABLED, wrap=ctk.WORD)
log_text.grid(row=5, column=0, padx=10, pady=(5, 0), sticky="nsew")
window.grid_rowconfigure(5, weight=1)

# --- 6. Status Bar ---
status_label = ctk.CTkLabel(window, text="Status: Inicjalizacja...", font=ctk.CTkFont(size=11), anchor="w")
status_label.grid(row=6, column=0, padx=10, pady=5, sticky="ew")
help_button = ctk.CTkButton(window, text="?", command=show_help, font=ctk.CTkFont(size=12, weight='bold'), width=20, height=20, fg_color="gray40", hover_color="gray50")
help_button.place(relx=1.0, x=-10, y=10, anchor="ne")


# === Uruchomienie aplikacji ===
if __name__ == "__main__":
    try:
        import rtlsdr, sounddevice, numpy, scipy, customtkinter
        log_message_gui("Aplikacja uruchomiona. Sprawdzam zależności...")
        log_message_gui(f"Numpy: {np.__version__}, Scipy: {scipy.__version__}")
        log_message_gui(f"SoundDevice: {sd.__version__}")
        log_message_gui(f"CustomTkinter: {customtkinter.__version__}")
        update_status("Gotowy")
        window.mainloop()
    except ImportError as e:
         missing_lib = str(e).split("'")[-2]
         print(f"Brak Biblioteki: {missing_lib}")
         messagebox.showerror("Brak Biblioteki", f"Nie znaleziono wymaganej biblioteki: '{missing_lib}'\n\nZainstaluj ją używając:\npip install {missing_lib} --break-system-packages")
    except Exception as general_e:
        print(f"Błąd Startowy: {general_e}")
        messagebox.showerror("Błąd Startowy", f"Wystąpił nieoczekiwany błąd podczas startu:\n{general_e}")
