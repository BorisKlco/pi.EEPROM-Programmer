import RPi.GPIO as GPIO
import time

# -------
# A10-A0 - was build for 28C16 EEPROM with 10 address inputs.
# by inserting GPIO num for A14-A11 to front of ADDR_PIN[]
# script should work for bigger 28C models.
ADDR_PIN = [16, 12, 26, 19, 13, 6, 5, 0, 11, 9, 10]
EEPROM_SIZE = len(ADDR_PIN)
# -------
# D7-D0 (I/O)
DATA_PIN = [7, 8, 25, 24, 23, 22, 27, 17]
# -------
WE = 20
OE = 21
# -------
WRITE_DATA = [
    0x81,
    0xCF,
    0x92,
    0x86,
    0xCC,
    0xA4,
    0xA0,
    0x8F,
    0x80,
    0x84,
    0x88,
    0xE0,
    0xB1,
    0xC2,
    0xB0,
    0xB8,
]
# -------
GPIO.setmode(GPIO.BCM)


# --------May the Force be with you------#
# ---- Ben Eater Our Lord and Savior 🙏--#


def setAddress(addr):
    # Pleas dont use negative numbers
    if addr > 2047:
        print("\nOverflow of 28C16 memory size, setting 0x7ff\n")
        return [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    result = []
    for i in range(EEPROM_SIZE):
        try:
            result.append(1 if (addr & (1 << (EEPROM_SIZE - 1 - i))) != 0 else 0)
        except:
            result.insert(0, 0)

    return result


def setData(data):
    # Pleas dont use negative numbers
    if data > 255:
        print("\nOverflow of data size, setting 0xff\n")
        return [1, 1, 1, 1, 1, 1, 1, 1]
    result = []
    for i in range(8):
        result.append(1 if (data & (1 << (7 - i))) != 0 else 0)
    return result


def read(addr):
    GPIO.setup((WE, OE), GPIO.OUT)
    GPIO.output(WE, 1)
    GPIO.output(OE, 0)
    BYTE_ADDR = setAddress(addr)
    BYTE_DATA = []

    for i, pin in enumerate(ADDR_PIN):
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, BYTE_ADDR[i])

    time.sleep(0.001)

    for pin in DATA_PIN:
        GPIO.setup(pin, GPIO.IN)
    time.sleep(0.001)

    for pin in DATA_PIN:
        BYTE_DATA.append(GPIO.input(pin))

    time.sleep(0.001)

    return BYTE_DATA


def write(addr, data):
    GPIO.setup((WE, OE), GPIO.OUT)
    GPIO.output(WE, 1)
    GPIO.output(OE, 1)
    BYTE_ADDR = setAddress(addr)
    BYTE_DATA = setData(data)

    for i, pin in enumerate(ADDR_PIN):
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, BYTE_ADDR[i])

    for i, pin in enumerate(DATA_PIN):
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, BYTE_DATA[i])

    time.sleep(0.001)
    GPIO.output(WE, 0)
    # 1k ns
    time.sleep(0.000001)
    GPIO.output(WE, 1)
    time.sleep(0.01)


# --------May the Force be with you------#
# ---- Ben Eater Our Lord and Savior 🙏--#
def printContents():
    for base in range(0, 256, 16):
        data = [0] * 16
        for offset in range(0, 16):
            result = read(base + offset)
            rep = 0
            for num in result:
                rep = (rep << 1) + num
            data[offset] = rep
        buf = (
            "%03x: %02x %02x %02x %02x %02x %02x %02x %02x   %02x %02x %02x %02x %02x %02x %02x %02x"
            % (
                base,
                data[0],
                data[1],
                data[2],
                data[3],
                data[4],
                data[5],
                data[6],
                data[7],
                data[8],
                data[9],
                data[10],
                data[11],
                data[12],
                data[13],
                data[14],
                data[15],
            )
        )
        print(buf)
    time.sleep(0.1)


def prog(start_addr):
    print("Writing data to addr", start_addr, "\n")
    for addr, data in enumerate(WRITE_DATA):
        write(start_addr + addr, data)
    print("Done...")
    time.sleep(0.1)


# --------May the Force be with you------#
# ---- Ben Eater Our Lord and Savior 🙏--#

# prog(0)
printContents()

# ---🧹---#
GPIO.cleanup()
