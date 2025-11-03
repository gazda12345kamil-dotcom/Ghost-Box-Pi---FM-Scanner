# Ghost Box Pi - PRO (v5.1)
---

This is an update for the `Ghost Box Pi PRO v4` project, introducing a complete overhaul of the audio processing engine (DSP) and crucial stability fixes.

The goal of this update is to drastically improve the listening quality and comfort, and to eliminate stability bugs present in v4.

## 🚀 What's new in v5.1 (compared to v4)?

Version 5.1 consists of two major upgrades: **a new audio engine (v5.0)** and **bug fixes (v5.1)**.

---

### 🎧 Audio Engine (DSP+) Upgrades

The base v4 version used simple audio normalization (`audio / max_val`), which caused harsh volume jumps ("pumping") and fatiguing, sharp noise. This has been completely replaced with a studio-grade audio pipeline:

1.  **Automatic Gain Control (AGC):**
    * **The Problem (v4):** Loud stations would "explode" in volume, and the background noise was deafening.
    * **The Solution (v5.1):** An **AGC** algorithm has been implemented. It smoothly equalizes volume levels. Quiet signals are automatically amplified, and sudden loud transmissions are attenuated, ensuring a stable and comfortable listening experience.

2.  **"Voice" Audio Filter (300-3400 Hz):**
    * **The Problem (v4):** The raw audio contained fatiguing, high-pitched sibilance (hiss) and low-end hum/rumble.
    * **The Solution (v5.1):** A Butterworth band-pass filter focused purely on the human voice spectrum has been added. This **drastically reduces sibilant noise** and improves the clarity of potential EVPs.

3.  **"Click" Elimination (Stateful Filtering):**
    * **The Problem (v4):** With every frequency hop, an audible "click" or "pop" could be heard at the junction of audio blocks.
    * **The Solution (v5.1):** **Stateful filtering** (`lfilter_zi`) has been implemented, which ensures perfectly continuous audio processing. **All clicks and pops at block junctions have been eliminated.**

---

### 🛠️ Bug Fixes & Stability (v5.1)

Version v4 had two bugs that could interfere with the application's usability:

1.  **Fixed SDR Resource Locking (Critical):**
    * **The Problem (v4):** When closing the window, the application would not always correctly release the RTL-SDR receiver. This would cause a "Device or resource busy" error on the next launch, forcing a computer restart or an SDR re-plug.
    * **The Solution (v5.1):** The closing procedure (`on_closing`) has been rewritten and **now guarantees the SDR resource is properly released** every time.

2.  **Fixed Record (REC) Button State Bug:**
    * **The Problem (v4):** If the user pressed "REC" but recording failed to start (e.g., due to a full disk or permissions error), the button would still change to "STOP", misleading the user into thinking a recording was in progress.
    * **The Solution (v5.1):** Error handling has been added. If recording fails, the button immediately reverts to "REC 🔴" and an error message is printed to the log.

---

## Main Features (v5.1)

* **New Audio Engine (AGC + Voice Filter)**
* **Improved Stability** (no resource leaks)
* Session Recording (REC) to `.wav`
* Live S-Meter (Signal Strength Indicator)
* Save/Load Settings (`config.json`)
* Multi-Band Scanning (FM, AIR, CB, AM, WX, 2M-HAM)
* Sequential and Random ("Mix") Scan Modes
* Adjustable Squelch
