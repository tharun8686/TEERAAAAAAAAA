[CmdletBinding()]
param([switch]$CheckOnly)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$projectRoot = Split-Path -Parent $PSScriptRoot
$logPath = Join-Path $PSScriptRoot 'arduino-setup.log'
$espIndex = 'https://espressif.github.io/arduino-esp32/package_esp32_index.json'
$espCore = 'esp32:esp32@3.3.11'
$libraries = @(
    'LoRa@0.8.0', 'ArduinoJson@7.4.3',
    'Adafruit BME680 Library@2.0.6', 'Adafruit MPU6050@2.2.9',
    'Adafruit Unified Sensor@1.1.15', 'Adafruit BusIO@1.17.4',
    'TinyGPSPlus@1.0.3'
)

function Write-Step([string]$Message) {
    Write-Host "`n==> $Message" -ForegroundColor Cyan
    Add-Content -LiteralPath $logPath -Value "[$(Get-Date -Format s)] $Message"
}

function Find-ArduinoCli {
    $command = Get-Command arduino-cli.exe -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }
    $candidates = @(
        (Join-Path $env:LOCALAPPDATA 'Programs\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe'),
        (Join-Path $env:ProgramFiles 'Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe'),
        (Join-Path ${env:ProgramFiles(x86)} 'Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe')
    )
    return $candidates | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -First 1
}

function Invoke-Cli([string[]]$Arguments) {
    & $script:cli @Arguments 2>&1 | Tee-Object -FilePath $logPath -Append
    if ($LASTEXITCODE -ne 0) { throw "Arduino command failed: $($Arguments -join ' ')" }
}

function Install-ArduinoIde {
    $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
    if (-not $winget) {
        throw 'Arduino IDE is missing and Windows Package Manager is unavailable. Install App Installer from Microsoft Store, then run this file again.'
    }
    Write-Step 'Installing Arduino IDE from Windows Package Manager'
    & $winget.Source install --exact --id ArduinoSA.IDE.stable --accept-package-agreements --accept-source-agreements --silent
    if ($LASTEXITCODE -ne 0) { throw 'Arduino IDE installation failed.' }
}

function Test-UsbDrivers {
    Write-Step 'Checking connected ESP32 USB devices and drivers'
    $devices = Get-CimInstance Win32_PnPEntity | Where-Object { $_.PNPDeviceID -match 'VID_(303A|10C4|1A86)' }
    if (-not $devices) {
        Write-Host 'No supported ESP32 USB device is connected.' -ForegroundColor Yellow
        Write-Host 'Plug in both boards, wait for Windows Update, then rerun this installer to check drivers.'
        return
    }
    foreach ($device in $devices) {
        $kind = if ($device.PNPDeviceID -match 'VID_303A') { 'Espressif native USB (Windows driver)' }
            elseif ($device.PNPDeviceID -match 'VID_10C4') { 'Silicon Labs CP210x USB-to-UART' }
            else { 'WCH CH340/CH341 USB-to-UART' }
        $ok = $device.ConfigManagerErrorCode -eq 0
        $state = if ($ok) { 'READY' } else { 'DRIVER REQUIRED' }
        Write-Host ("{0}: {1} - {2}" -f $kind, $device.Name, $state)
        if (-not $ok) {
            if ($kind -like '*CP210x*') {
                Write-Host 'Official driver: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers' -ForegroundColor Yellow
            } elseif ($kind -like '*CH340*') {
                Write-Host 'Use the signed driver from WCH or your ESP32 board vendor.' -ForegroundColor Yellow
            }
            throw 'Windows detects an ESP32 USB adapter but its driver is not ready.'
        }
    }
}

Set-Content -LiteralPath $logPath -Value "TerraEdge Arduino setup $(Get-Date -Format s)"
Write-Host 'TerraEdge Arduino Setup' -ForegroundColor Green
Write-Host 'Target boards: ESP32-S3 sender and standard ESP32 receiver'
$script:cli = Find-ArduinoCli
if (-not $script:cli -and -not $CheckOnly) {
    Install-ArduinoIde
    $script:cli = Find-ArduinoCli
}
if (-not $script:cli) { throw 'arduino-cli.exe was not found after Arduino IDE installation.' }
Write-Step "Using Arduino tools at $script:cli"
Invoke-Cli @('version')

if (-not $CheckOnly) {
    Write-Step 'Updating Arduino package and library indexes'
    Invoke-Cli @('core', 'update-index', '--additional-urls', $espIndex)
    Invoke-Cli @('lib', 'update-index')
    Write-Step "Installing ESP32 board package $espCore"
    Invoke-Cli @('core', 'install', $espCore, '--additional-urls', $espIndex)
    foreach ($library in $libraries) {
        Write-Step "Installing $library"
        Invoke-Cli @('lib', 'install', $library)
    }
}

$work = Join-Path $env:TEMP 'TerraEdge-Arduino-Verify'
New-Item -ItemType Directory -Force -Path (Join-Path $work 'SENDER'), (Join-Path $work 'RECEIVER') | Out-Null
Copy-Item -LiteralPath (Join-Path $projectRoot 'SENDER.ino') -Destination (Join-Path $work 'SENDER\SENDER.ino') -Force
Copy-Item -LiteralPath (Join-Path $projectRoot 'RECEIVER.ino') -Destination (Join-Path $work 'RECEIVER\RECEIVER.ino') -Force
Write-Step 'Compiling SENDER.ino for ESP32-S3'
Invoke-Cli @('compile', '--fqbn', 'esp32:esp32:esp32s3:CDCOnBoot=cdc', (Join-Path $work 'SENDER'))
Write-Step 'Compiling RECEIVER.ino for standard ESP32'
Invoke-Cli @('compile', '--fqbn', 'esp32:esp32:esp32', (Join-Path $work 'RECEIVER'))
Test-UsbDrivers
Write-Step 'Installation and sketch verification complete'
Write-Host "`nOpen SENDER.ino with board 'ESP32S3 Dev Module'." -ForegroundColor Green
Write-Host "Open RECEIVER.ino with board 'ESP32 Dev Module'."
Write-Host 'Select the matching COM port before Upload.'
Write-Host "Log saved to $logPath"
