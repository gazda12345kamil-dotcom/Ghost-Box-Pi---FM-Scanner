# Ghost Box Pi - PRO (v5.1)
---

Jest to aktualizacja dla projektu `Ghost Box Pi PRO v4`, która wprowadza kompletną przebudowę silnika przetwarzania dźwięku (DSP) oraz kluczowe poprawki stabilności.

Celem tej aktualizacji jest drastyczna poprawa jakości i komfortu odsłuchu oraz wyeliminowanie błędów stabilności obecnych w v4.

## 🚀 Co nowego w v5.1 (względem v4)?

Wersja v5.1 to dwie duże modernizacje: **nowy silnik audio (v5.0)** oraz **poprawki błędów (v5.1)**.

---

### 🎧 Ulepszenia Silnika Audio (DSP+)

Wersja bazowa v4 używała prostej normalizacji audio (`audio / max_val`), co powodowało gwałtowne skoki głośności ("pompowanie") i męczący, ostry szum. Zostało to całkowicie zastąpione przez potok audio klasy studyjnej:

1.  **Automatyczna Kontrola Wzmocnienia (AGC):**
    * **Problem (v4):** Głośne stacje "eksplodowały" głośnością, a szum tła był ogłuszający.
    * **Rozwiązanie (v5.1):** Zaimplementowano algorytm **AGC**, który płynnie wyrównuje poziomy głośności. Ciche sygnały są automatycznie wzmacniane, a nagłe głośne transmisje są ściszane, zapewniając stabilny i komfortowy odsłuch.

2.  **Filtr Głosowy (300-3400 Hz):**
    * **Problem (v4):** Surowy dźwięk zawierał męczące, wysokie syki i niskie buczenie.
    * **Rozwiązanie (v5.1):** Dodano filtr pasmowy (Butterwortha) skupiony wyłącznie na paśmie ludzkiego głosu. **Drastycznie redukuje to sykliwy szum** i poprawia czytelność potencjalnych EVP.

3.  **Eliminacja "Klików" (Filtrowanie Stanowe):**
    * **Problem (v4):** Przy każdym przeskoku częstotliwości, na łączeniu bloków audio, słyszalny był "trzask" lub "klik".
    * **Rozwiązanie (v5.1):** Wdrożono **filtrowanie stanowe** (`lfilter_zi`), które zapewnia idealnie ciągłe przetwarzanie dźwięku. **Wszystkie trzaski na łączeniach zostały wyeliminowane.**

---

### 🛠️ Poprawki Błędów i Stabilności (v5.1)

Wersja v4 posiadała dwa błędy, które mogły uniemożliwić korzystanie z aplikacji:

1.  **Naprawiono Blokowanie Zasobu SDR (Krytyczne):**
    * **Problem (v4):** Po zamknięciu okna, aplikacja nie zawsze poprawnie zwalniała odbiornik RTL-SDR. Przy ponownej próbie uruchomienia, program zgłaszał błąd "Device or resource busy". Wymagało to restartu komputera lub ponownego podłączenia SDR.
    * **Rozwiązanie (v5.1):** Procedura zamykania (`on_closing`) została przepisana i **gwarantuje zwolnienie zasobu SDR** za każdym razem.

2.  **Naprawiono Błąd Przycisku Nagrywania (REC):**
    * **Problem (v4):** Jeśli użytkownik nacisnął "REC", ale nagrywanie nie mogło się rozpocząć (np. z powodu braku uprawnień do zapisu lub pełnego dysku), przycisk i tak zmieniał się na "STOP", wprowadzając w błąd, że nagrywanie trwa.
    * **Rozwiązanie (v5.1):** Dodano obsługę błędów. Jeśli nagrywanie się nie powiedzie, przycisk natychmiast wraca do stanu "REC 🔴", a w logach pojawia się informacja o błędzie.

---

## Główne Funkcje (v5.1)

* **Nowy silnik audio (AGC + Filtr Głosowy)**
* **Poprawiona stabilność** (brak wycieków zasobów)
* Nagrywanie sesji (REC) do `.wav`
* Sygnałomierz (S-Meter)
* Zapis/Wczytywanie ustawień (`config.json`)
* Skanowanie wielopasmowe (FM, AIR, CB, AM, WX, 2M-HAM)
* Tryb Sekwencyjny i Losowy ("Mix")
* Regulowany Squelch
