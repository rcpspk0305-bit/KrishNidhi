import time
from machine import Pin

try:
    from machine import SoftI2C as I2C
except ImportError:
    from machine import I2C

# PCF8574 pin mapping to HD44780 LCD
# P0: RS, P1: RW, P2: EN, P3: Backlight, P4-P7: Data D4-D7
MASK_RS = 0x01
MASK_RW = 0x02
MASK_EN = 0x04
MASK_BL = 0x08


class I2cLcd:
    def __init__(self, i2c, addr=0x27, num_lines=2, num_columns=16):
        self.i2c = i2c
        self.addr = addr
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.backlight = MASK_BL

        time.sleep_ms(50)

        # 4-bit initialization per HD44780 datasheet
        self._write_nibble(0x30)
        time.sleep_ms(5)
        self._write_nibble(0x30)
        time.sleep_us(200)
        self._write_nibble(0x30)
        time.sleep_ms(1)
        self._write_nibble(0x20)  # 4-bit mode
        time.sleep_ms(1)

        # Function set: 4-bit, 2 lines, 5x8 font
        self.hal_write_command(0x28)
        # Display control: display on, cursor off, blink off
        self.hal_write_command(0x0C)
        # Clear display
        self.clear()
        # Entry mode: increment cursor, no display shift
        self.hal_write_command(0x06)

    def _write_byte(self, val):
        self.i2c.writeto(self.addr, bytearray([val | self.backlight]))

    def _write_nibble(self, val):
        self._write_byte(val | MASK_EN)
        time.sleep_us(2)
        self._write_byte(val & ~MASK_EN)
        time.sleep_us(50)

    def hal_write_command(self, cmd):
        high = cmd & 0xF0
        low = (cmd << 4) & 0xF0
        self._write_nibble(high)
        self._write_nibble(low)
        if cmd <= 3:
            time.sleep_ms(2)

    def hal_write_data(self, data):
        high = (data & 0xF0) | MASK_RS
        low = ((data << 4) & 0xF0) | MASK_RS
        self._write_nibble(high)
        self._write_nibble(low)

    def clear(self):
        self.hal_write_command(0x01)
        time.sleep_ms(2)

    def move_to(self, col, row):
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        addr = col + row_offsets[row % len(row_offsets)]
        self.hal_write_command(0x80 | addr)

    def putstr(self, string):
        for char in string:
            self.hal_write_data(ord(char))

    def print_line(self, row, text):
        """Prints a padded line to prevent visual artifacts."""
        self.move_to(0, row)
        truncated = text[: self.num_columns]
        padded = truncated + (" " * (self.num_columns - len(truncated)))
        self.putstr(padded)


def init_lcd(scl_pin=5, sda_pin=4):
    """
    Initializes I2C LCD on specified GPIO pins (default: D1=GPIO5, D2=GPIO4).
    Scans for addresses 0x27 and 0x3F.
    Returns I2cLcd instance if found, or None if no display is connected.
    """
    try:
        i2c = I2C(scl=Pin(scl_pin), sda=Pin(sda_pin), freq=100000)
        devices = i2c.scan()
        print("[I2C] Scanned addresses:", [hex(d) for d in devices])

        for addr in [0x27, 0x3F]:
            if addr in devices:
                lcd = I2cLcd(i2c, addr=addr, num_lines=2, num_columns=16)
                lcd.print_line(0, "Smart Plant IoT")
                lcd.print_line(1, "Initializing...")
                print(f"[LCD] 16x2 LCD initialized at {hex(addr)}")
                return lcd

        print("[LCD] No 16x2 I2C LCD found (running headless)")
        return None
    except Exception as err:
        print("[LCD] Warning: LCD initialization failed:", err)
        return None
