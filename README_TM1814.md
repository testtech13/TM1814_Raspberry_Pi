# TM1814 Driver Setup Guide for Raspberry Pi

This project now supports TM1814 LED strips on the Raspberry Pi using the SPI interface, which provides superior stability and timing compared to PWM/GPIO toggling.

## Hardware Requirements

The driver supports three interfaces. **SPI is strongly recommended** for stability and system integration.

### 1. Primary Interface: SPI (Recommended)
*   **Pin**: GPIO 10 (SPI0 MOSI) - Pin 19 on header.
*   **Pros**: Best stability, no conflict with onboard audio.
*   **Cons**: Requires enabling SPI and increasing buffer size.

### 2. Backup Interface: PWM
*   **Pin**: GPIO 18 (PWM0) - Pin 12 on header. (Also supports GPIO 12, 13, 19).
*   **Pros**: Good stability.
*   **Cons**: **Disables onboard analog audio** (headphone jack).

### 3. Backup Interface: PCM
*   **Pin**: GPIO 21 (PCM DOUT) - Pin 40 on header.
*   **Pros**: Good stability.
*   **Cons**: Conflicts with I2S digital audio HATs.

### Level Shifter & Inverter (Required for all interfaces)
*   **Recommended**: Use a hardware inverter (e.g., 74HCT04 or 74HCT14) to invert the signal and shift it to 5V.
*   **Alternative**: If connecting directly (not recommended due to voltage levels), you must use software inversion.

## Configuration

The driver is configured in `config.py`.

*   Set `LED_DRIVER_TYPE = 'TM1814'` to enable this driver.
*   **Select Interface**:
    *   **SPI**: Set `LED_PIN = 10`
    *   **PWM**: Set `LED_PIN = 18`
    *   **PCM**: Set `LED_PIN = 21`
*   **Inversion**:
    *   If using a **hardware inverter**, set `LED_INVERT = False`.
    *   If **no hardware inverter**, set `LED_INVERT = True`.

## System Configuration (Crucial Steps)

### For SPI Users (Recommended)

To ensure the driver works correctly via SPI, you must configure the Raspberry Pi system.

#### 1. Enable SPI

Run `sudo raspi-config`, go to **Interface Options** -> **SPI**, and enable it.
Or add `dtparam=spi=on` to `/boot/config.txt`.

#### 2. Increase SPI Buffer Size (Required for >300 LEDs)

The default SPI buffer size (4KB) is sufficient for up to approximately 300 RGBW LEDs. If you are using more than 300 LEDs, you must increase this buffer to prevent flickering or partial updates.

1.  Open `/boot/cmdline.txt` for editing:
    ```bash
    sudo nano /boot/cmdline.txt
    ```
2.  Add `spidev.bufsiz=65536` to the end of the line. **Do not create a new line**; add it to the existing line, separated by a space.
    
    Example:
    ```text
    console=serial0,115200 console=tty1 root=PARTUUID=... rootfstype=ext4 fsck.repair=yes rootwait spidev.bufsiz=65536
    ```
3.  Reboot the Pi:
    ```bash
    sudo reboot
    ```

### For PWM Users

*   You must disable analog audio to use GPIO 18 for LEDs.
*   Edit `/boot/config.txt` and comment out `dtparam=audio=on` (change to `#dtparam=audio=on`).
*   Reboot.

## Troubleshooting

*   **Flickering or Random Colors**: Check your ground connection. Ensure the Pi ground and LED power supply ground are connected.
*   **"Demo Mode" (Rainbow cycling)**: This usually means the TM1814 is seeing a floating input or the idle state is incorrect. Verify your inversion setting. If `LED_INVERT` is True, the line should idle High (which might require a pull-up if the Pi floats it, but SPI MOSI usually drives Low when idle, hence why hardware inversion is better).
*   **Wrong Colors**: TM1814 is RGBW. If colors are swapped (e.g., Red is Green), you may need to adjust the byte packing in `tm1814_driver.py` or change the `STRIP_TYPE` constant.
