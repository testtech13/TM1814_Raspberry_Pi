import time

try:
    from rpi_ws281x import PixelStrip, Color, ws
except ImportError:
    # Mock classes for development on non-Pi systems
    class ws:
        SK6812_STRIP_RGBW = 0x18100800 # Dummy value

    class PixelStrip:
        def __init__(self, num, pin, freq_hz=800000, dma=10, invert=False, brightness=255, channel=0, strip_type=None):
            self.num = num
            self.brightness = brightness
            self.pixels = [0] * num

        def begin(self):
            pass

        def numPixels(self):
            return self.num

        def setPixelColor(self, n, color):
            if 0 <= n < self.num:
                self.pixels[n] = color

        def show(self):
            pass
        
        def setBrightness(self, brightness):
            self.brightness = brightness

class TM1814Driver:
    """
    Driver for TM1814 LED strips using SPI, PWM, or PCM interfaces on Raspberry Pi.
    
    The TM1814 is a 4-channel (RGBW) constant-current LED driver.
    
    Interface Options:
    1. SPI (Recommended): Uses GPIO 10 (MOSI). Best stability, independent of audio.
    2. PWM: Uses GPIO 18 or 12 (PWM0), 13 or 19 (PWM1). Good stability, but conflicts with analog audio.
    3. PCM: Uses GPIO 21. Good stability, but conflicts with I2S digital audio.
    
    Key Features:
    - Supports RGBW (4-channel) color data.
    - Handles signal inversion (required for TM1814).
    
    System Requirements:
    - For SPI: Enable SPI (`dtparam=spi=on`) and increase buffer size.
    - For PWM: Disable analog audio if using GPIO 18.
    - For PCM: Ensure no I2S audio devices are active.
    """
    def __init__(self, num_pixels, brightness=255, invert=True, pin=10, dma=10, channel=0):
        """
        Initialize the TM1814 driver.
        
        :param num_pixels: Total number of LEDs in the strip.
        :param brightness: Global brightness (0-255).
        :param invert: Signal inversion flag.
            - Set to True if connecting directly or using a non-inverting level shifter.
            - Set to False if using a hardware inverter (e.g., 74HCT04).
        :param pin: GPIO pin number (BCM).
            - 10: SPI (MOSI) - Recommended
            - 18, 12, 13, 19: PWM
            - 21: PCM
        :param dma: DMA channel (default 10).
        :param channel: PWM/SPI channel (0 or 1).
        """
        # TM1814 Configuration
        self.LED_COUNT = num_pixels
        self.LED_PIN = pin
        self.LED_FREQ_HZ = 800000 # 800kHz is the standard frequency for TM1814
        self.LED_DMA = dma
        self.LED_INVERT = invert
        self.LED_CHANNEL = channel
        
        # The TM1814 is a 4-channel (RGBW) driver.
        # The rpi_ws281x library doesn't have a native 'TM1814' type, but 
        # SK6812_STRIP_RGBW uses the same 32-bit structure and similar timing.
        # Note: If colors are swapped (e.g. Red is Green), try SK6812_STRIP_GRBW.
        self.STRIP_TYPE = ws.SK6812_STRIP_RGBW
        
        self.strip = PixelStrip(
            self.LED_COUNT,
            self.LED_PIN,
            self.LED_FREQ_HZ,
            self.LED_DMA,
            self.LED_INVERT,
            brightness,
            self.LED_CHANNEL,
            self.STRIP_TYPE
        )
        
    def begin(self):
        self.strip.begin()

    def numPixels(self):
        return self.strip.numPixels()

    def setPixelColor(self, n, color):
        """
        Set pixel color. 
        Compatible with rpi_ws281x setPixelColor.
        """
        self.strip.setPixelColor(n, color)

    def set_pixel(self, index, r, g, b, w=0):
        """
        Set the color of a specific pixel using individual RGBW components.
        
        The TM1814 protocol expects 32 bits of data per pixel.
        This method packs the Red, Green, Blue, and White components into a single
        32-bit integer required by the underlying rpi_ws281x library.
        
        :param index: The index of the pixel to set (0-based).
        :param r: Red component (0-255).
        :param g: Green component (0-255).
        :param b: Blue component (0-255).
        :param w: White component (0-255).
        """
        # Pack color into a 32-bit integer: (W << 24) | (R << 16) | (G << 8) | B
        # This assumes the strip type is configured as RGBW.
        # If your colors are wrong, you can adjust the shift order here or change STRIP_TYPE.
        color_int = (w << 24) | (r << 16) | (g << 8) | b
        self.strip.setPixelColor(index, color_int)

    def show(self):
        """
        Update the LED strip with the data currently in the buffer.
        This triggers the SPI transfer to send data to the LEDs.
        """
        self.strip.show()

    def clear(self):
        """
        Turn off all LEDs.
        Sets all pixels to 0 (black) and updates the strip.
        """
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, 0)
        self.show()
        
    def setBrightness(self, brightness):
        """
        Set the global brightness of the strip.
        
        :param brightness: Brightness level (0-255).
        Note: This scales the values on the next setPixelColor call or update,
        depending on the library version.
        """
        self.strip.setBrightness(brightness)

    def cleanup(self):
        """Clean up resources."""
        # rpi_ws281x doesn't have a specific cleanup, but we can clear the strip
        self.clear()
