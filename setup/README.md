# One-click Arduino setup for Windows

On Windows 10/11, clone or download this project, extract it, and double-click
`INSTALL_ARDUINO_WINDOWS.bat`. Keep the internet connected. The script:

1. installs Arduino IDE through Windows Package Manager when it is missing;
2. installs Espressif ESP32 core 3.3.11;
3. installs the pinned libraries required by both sketches;
4. compiles both sketches for the intended boards; and
5. checks attached ESP32 USB devices and reports driver status.

The S3 sender normally uses native Espressif USB with a Windows inbox driver. A
standard ESP32 receiver may contain a CP210x or CH340/CH341 USB-to-serial chip.
Because that chip is selected by the board manufacturer, no safe universal driver
package exists. Plug both boards in before running setup. Windows Update commonly
installs the correct signed driver. If it does not, the script reports the detected
chip and identifies the official driver source. Avoid third-party driver sites.

The installer does not upload automatically because selecting the wrong COM port
could overwrite another connected board. After setup, open each root `.ino` file
separately in Arduino IDE:

- `SENDER.ino`: **ESP32S3 Dev Module**, USB CDC On Boot enabled.
- `RECEIVER.ino`: **ESP32 Dev Module**.

Select the matching COM port and click Upload. The setup log is written to
`setup/arduino-setup.log` and is ignored by Git.
