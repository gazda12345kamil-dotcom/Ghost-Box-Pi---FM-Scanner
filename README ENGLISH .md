Ghost Box Pi - Radio Scanner (FM/AM/AIR)An application for scanning radio bands (FM, AM, AIR, CB, and more) using an RTL-SDR v4 on a Raspberry Pi. Ghost Box Pi allows for automatic switching between radio stations with adjustable speed, volume, and advanced noise control.📦 Available VersionsThe project includes three versions of the application to choose from:1️⃣ Basic Version (ghostbox_fm.py)A classic, simple version of Ghost Box (FM only):✅ Sequential scanning of the FM band (87.5-108 MHz)✅ Scan speed adjustment (50-500 ms)✅ Volume control (0-100%)✅ Simple interface (Tkinter)Recommended for: Beginners who want simple, FM-only operation.2️⃣ Advanced Version (ghostbox_fm_V2.py)An extended version (FM only) with additional features:✅ All features of the basic version✅ Squelch - automatic muting of noise✅ Mix Mode (Random) - scans FM in a random order✅ Better control over audioRecommended for: Users who want advanced scan control on the FM band only.3️⃣ PRO Version (v4) (ghostbox_pi_PRO_v4.py)A completely rebuilt, multi-band version with a modern interface:✅ Modern Interface (CustomTkinter)✅ Multi-Band Scanning (FM, AM, AIR, CB, WX, 2M-HAM)✅ Band Mixing - select any combination of bands to scan (e.g., FM + AIR)✅ Advanced Squelch - precise squelch based on signal power✅ Multiple Demodulators (WBFM, AM, NBFM) for the best sound quality✅ Audio Recording (REC) - save sessions to .wav files✅ S-Meter - live signal strength indicator✅ Saves Settings - the application remembers your last settingsRecommended for: Advanced users who want full control and access to all bands.🤔 Which version to choose?FeatureBasicAdvanced (V2)PRO Version (v4)Ease of Use⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐Graphical InterfaceStandard (Tkinter)Standard (Tkinter)Modern (CustomTkinter)FM Scanning✅✅✅Multi-Band Scanning❌❌✅ (AM, AIR, CB…)Band Mixing❌❌✅ (Any combination)Squelch❌✅ (Basic)✅ (Advanced)Random Mode (Mix)❌✅ (FM Only)✅ (On selected bands)Audio Recording (REC)❌❌✅S-Meter❌❌✅Save Settings❌❌✅💡 Recommendation: If you only want to scan FM, choose V2. If you want full capabilities, scanning AM, AIR, and mixing bands, choose the PRO Version (v4).Hardware RequirementsRaspberry Pi 5 (recommended) or Raspberry Pi 4RTL-SDR v4 (USB dongle) - ORIGINAL ONLY! ⚠️Official Raspberry Pi 5 Power Supply (5V/5A USB-C)Speaker/headphones (HDMI, 3.5mm Jack, or Bluetooth)USB 3.0 port (blue) - recommended for the RTL-SDR⚠️ Where to buy an original RTL-SDR v4?VERY IMPORTANT: There are many counterfeit RTL-SDRs on the market that may not work!Official Stores:🔗 List of authorized resellers: https://www.rtl-sdr.com/buy-rtl-sdr-dvb-t-dongles/How to recognize an original RTL-SDR Blog v4:✅ Metal case (blue or silver)✅ “RTL-SDR Blog” logo on the case✅ SMA connector (screw-on antenna)✅ Price around $35-45 USDSigns of a counterfeit:❌ No “RTL-SDR Blog” logo❌ Plastic case❌ Price below $25 USD❌ Seller not listed on the official websiteSystem RequirementsOperating System: Raspberry Pi OS (64-bit) - latest versionPython: 3.7 or newerSystem Libraries:RTL-SDR v4 driversPortAudioUSB librariesInstallationStep 1: System UpdateOpen a terminal and execute the following commands:sudo apt update
sudo apt upgrade -y
Step 2: Install RTL-SDR v4 DriversThe RTL-SDR v4 requires special drivers compiled from source.Remove old drivers:sudo apt purge -y ^librtlsdr* ^rtl-sdr*
Manually remove leftovers (copy the entire line carefully!):sudo rm -rvf /usr/lib/librtlsdr* /usr/include/rtl-sdr* /usr/local/lib/librtlsdr* /usr/local/include/rtl-sdr* /usr/local/include/rtl_* /usr/local/bin/rtl_*
Install build tools:sudo apt-get install libusb-1.0-0-dev git cmake pkg-config build-essential
Get the source code:git clone [https://github.com/rtlsdrblog/rtl-sdr-blog](https://github.com/rtlsdrblog/rtl-sdr-blog)
cd rtl-sdr-blog/
Build and compile:mkdir build
cd build
cmake ../ -DINSTALL_UDEV_RULES=ON
make
Install the drivers:sudo make install
sudo cp ../rtl-sdr.rules /etc/udev/rules.d/
sudo ldconfig
Blacklist the default DVB driver:echo 'blacklist dvb_usb_rtl28xxu' | sudo tee /etc/modprobe.d/blacklist-rtl-sdr.conf
Reboot the system:sudo reboot
Step 3: Verify InstallationAfter rebooting, plug in the RTL-SDR v4 to a USB port and run a test:rtl_test -t
Expected output: You should see device information (e.g., “RTL-SDR Blog V4”) and the test should complete successfully.Step 4: Install Python and PIPsudo apt install -y python3-pip
Step 5: Install Audio Dependenciessudo apt install -y libportaudio2 portaudio19-dev
Step 6: Install Python LibrariesChoose the set of libraries depending on the version you want to run.A) For Basic Version (v1) and Advanced Version (v2):pip install pyrtlsdr sounddevice numpy scipy --break-system-packages
B) For PRO Version (v4):This command installs everything you need: customtkinter for the UI and soundfile for recording.pip install pyrtlsdr sounddevice numpy scipy customtkinter soundfile --break-system-packages
Libraries being installed:pyrtlsdr - communication with RTL-SDRsounddevice - audio playbacknumpy - numerical operationsscipy - signal processingcustomtkinter - (FOR V4 ONLY) modern GUIsoundfile - (FOR V4 ONLY) saving .wav audio filesStep 7: Download the Application# Go back to the home directory
cd ~

# Clone the repository
git clone [https://github.com/gazda12345kamil-dotcom/ghost-box-pi.git](https://github.com/gazda12345kamil-dotcom/ghost-box-pi.git)
cd ghost-box-pi
Or download the code manually and save it as ghostbox_fm.py (Basic), ghostbox_fm_V2.py (Advanced), or ghostbox_pi_PRO_v4.py (PRO) on your desktop.Running the ApplicationBasic Version:python3 ghostbox_fm.py
Advanced Version (V2):python3 ghostbox_fm_V2.py
PRO Version (v4):python3 ghostbox_pi_PRO_v4.py
User Interface🎯 Basic Version (ghostbox_fm.py)After launching, you will see a window with:Frequency Display - current scanned FM frequencySpeed Slider - time spent on one frequency (50-500 ms)Volume Slider - controls the volume level (0-100%)START/STOP Buttons - scan controlLog Window - system and diagnostic messages🎯 Advanced Version (ghostbox_fm_V2.py)Includes all features of the basic version plus:Squelch Slider - signal strength threshold (0-100)Value 0 = off (you hear everything, including noise)Value 10-30 = standard use (mutes weak signals)Value 50+ = only strong stations“Mix (Random)” Checkbox - switches between sequential and random mode (FM only)Unchecked = scans in order (87.5 → 87.6 → 87.7…)Checked = scans random frequencies🎯 PRO Version (v4) (ghostbox_pi_PRO_v4.py)A modern interface with extended features:Modern Display - shows frequency and mode (AM/FM/NBFM)Band Checkboxes - Select bands to mix:FM (87.5-108 MHz)AM (531-1701 kHz)AIR (108.1-137 MHz)CB (26.965-27.405 MHz)WX (162.400-162.550 MHz)2M-HAM (144-146 MHz)S-Meter - Progress bar showing real-time signal strengthSpeed Slider - time per frequency (50-500 ms)Volume Slider - volume level (0-100%)Advanced Squelch Slider - precise power threshold (0-100)Control Buttons:START: Begins scanningSTOP: Stops scanningREC 🔴: Starts audio recording. The button changes to “STOP ⏹”. Clicking again stops recording and saves the .wav file“Mix (Random)” Checkbox - enables random mode for all selected bandsLog Window - Shows system messages, errors, and recording statusAutomatic Settings Save - volume, speed, and selected bands are remembered on exitTroubleshootingProblem 1: RTL-SDR not detectedSolution:Check the USB connection - use a USB 3.0 port (blue)Verify in the system: lsusb - look for ID 0bda:2838Check the power supply - use the official 5V/5A power adapterCheck if you have an original: https://www.rtl-sdr.com/buy-rtl-sdr-dvb-t-dongles/Unplug and replug the dongleCheck the blacklist: cat /etc/modprobe.d/blacklist-rtl-sdr.confProblem 2: No audioSolution:Select audio output:Right-click the speaker icon in the taskbarChoose the correct device (HDMI, Headphones, Bluetooth)Check system volume:Left-click the speaker iconEnsure the volume is not mutedTest sounddevice:python3
>>> import sounddevice as sd
>>> import numpy as np
>>> fs = 48000
>>> t = np.arange(fs * 3)
>>> audio = 0.5 * np.sin(2 * np.pi * 440 * t / fs)
>>> sd.play(audio.astype(np.float32), fs)
>>> sd.wait()
>>> exit()
Problem 3: Errors during library installationSolution:Ensure all system dependencies are installed (Step 2 and 5)Check your internet connectionUpgrade pip:pip install --upgrade pip --break-system-packages
Retry the library installation (Step 6)Problem 4: “Device or resource busy”Solution:Close all other SDR programs (SDR++, GQRX, CubicSDR)Unplug and replug the dongleAs a last resort: sudo rebootProblem 5: V2/V4 Version - I only hear silenceSolution:Check the Squelch slider - if it's set high, it might be muting all signalsSet Squelch to 0 (all the way to the left) to disable the functionGradually increase the value until you no longer hear static between stationsProblem 6: Error on V4 startup: “No module named ‘customtkinter’”Solution:You did not install the UI library. Run the command:pip install customtkinter --break-system-packages
Problem 7: Error on V4 startup: “No module named ‘soundfile’”Solution:You did not install the audio recording library. Run the command:pip install soundfile --break-system-packages
FeaturesBasic Version:✅ Full FM band scanning (87.5-108 MHz)✅ Adjustable scan speed (50-500 ms)✅ Real-time volume control✅ FM demodulation with automatic audio normalization✅ Graphical interface (Tkinter)✅ Event logging systemAdvanced Version (V2) - all of the above plus:✅ Squelch - noise muting on FM✅ Mix Mode (Random) - scans FM in a random order✅ Better control over audio qualityPRO Version (v4) - all V2 features plus:✅ Modern Interface (CustomTkinter)✅ Multi-Band Scanning (WBFM, AM, NBFM)✅ Full Band Mixing (selectable with checkboxes)✅ Advanced DSP Filtering for each mode✅ Precise Squelch based on signal power✅ Audio Session Recording (REC) - save to .wav files✅ Signal Strength Indicator (S-Meter) - visualizes signal power✅ Save and Load Settings - automatically remembers configurationConfigurationBand ConfigurationParameters can be adjusted directly in the .py files.V1 and V2 Versions (ghostbox_fm.py, ghostbox_fm_V2.py):# FM frequency range
FM_START_FREQ = 87.5e6
FM_END_FREQ = 108.0e6
FM_STEP = 0.1e6  # Scan step

# SDR Parameters
SDR_SAMPLE_RATE = 1.024e6
SDR_GAIN = 'auto'
AUDIO_SAMPLE_RATE = 48000
PRO Version v4 (ghostbox_pi_PRO_v4.py):# Band Definitions (WBFM, AM, NBFM)
BANDS_CONFIG = {
    "FM":      {'name': "FM",  'start': 87.5e6,  'end': 108.0e6, 'step': 0.1e6,  'mode': "WBFM"},
    "AIR":     {'name': "AIR", 'start': 108.1e6, 'end': 137.0e6, 'step': 0.025e6, 'mode': "AM"},
    "CB":      {'name': "CB",  'start': 26.965e6,'end': 27.405e6,'step': 0.01e6, 'mode': "AM"},
    "AM":      {'name': "AM", 'start': 531e3,   'end': 1701e3,  'step': 9e3,    'mode': "AM"},
    "WX":      {'name': "WX",  'start': 162.400e6,'end': 162.550e6,'step': 0.025e6,'mode': "NBFM"},
    "2M-HAM":  {'name': "2M-HAM",'start': 144.0e6, 'end': 146.0e6, 'step': 0.025e6,'mode': "NBFM"}
}

# SDR Parameters
SDR_SAMPLE_RATE = 1.024e6
SDR_GAIN = 'auto'
AUDIO_SAMPLE_RATE = 48000
Saved SettingsThe PRO (v4) version automatically creates a ghostbox_config.json file in the same folder. It stores:Last slider positions (volume, speed, squelch)State of the band checkboxesRandom (Mix) modeTo reset the settings to default, simply delete the ghostbox_config.json file.Required LibrariesPythontkinter - (for v1, v2) graphical interface (built into Python)pyrtlsdr - RTL-SDR interfacesounddevice - audio playbacknumpy - numerical calculationsscipy - signal processingcustomtkinter - (for v4) modern graphical interfacesoundfile - (for v4) saving .wav audio filesSystemlibrtlsdr - RTL-SDR v4 driverslibportaudio2 - audio librarylibusb-1.0-0 - USB communicationLicenseOpen Source - This project is free software. Anyone can use, modify, and distribute it without restrictions. The code is made available publicly for educational and community purposes.ContributingBug reports, suggestions, and pull requests are welcome! The project is open to all who want to help in its development.DisclaimerThe application is intended for educational and experimental purposesAdhere to local laws regarding the use of radio equipmentDo not listen to illegal radio transmissionsThe author is not responsible for improper use of the applicationContactIf you have questions or problems, open an Issue on GitHub.🔗 More info about RTL-SDR: https://www.rtl-sdr.comBuilt with ❤️ for the Raspberry Pi and SDR community
