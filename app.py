import RPi.GPIO as GPIO
import time

# -------
# A10-A0 - was build for 28C16 EEPROM with 10 address inputs.
# by inserting GPIO num for A14-A11 to front of ADDR_PIN[]
# script should work for bigger 28C models.
EEPROM_28C16 = True
ADDR_PIN = [27, 22, 10, 9, 11, 0, 5, 6, 13, 19, 26]
EEPROM_SIZE = len(ADDR_PIN)
# -------
# D7-D0 (I/O)
DATA_PIN = [25, 8, 7, 1, 12, 16, 20, 21]
# -------
WE = 2
OE = 3
# -------
#Cathode 0-fH
WRITE_DATA = [0x7E,0x30,0x6D,0x79,0x33,0x5B,0x5F,0x70,0x7F,0x7B,0x77,0x1F,0x4E,0x3D,0x4F,0x47]
# -------
GPIO.setmode(GPIO.BCM)


# --------May the Force be with you------#
# ---- Ben Eater Our Lord and Savior 🙏--#


def setAddress(addr, EEPROM_28C16):
    if addr > 2047 and EEPROM_28C16:
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

    time.sleep(0.01)
    GPIO.output(WE, 0)
    time.sleep(0.001)
    GPIO.output(WE, 1)
    time.sleep(0.01)


# --------May the Force be with you------#
# ---- Ben Eater Our Lord and Savior 🙏--#
def printContents():
    for base in range(0, 2048, 16):
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

def multiplexed():
    #Cathode 0-9
    digits = [0x7E, 0x30, 0x6D, 0x79, 0x33, 0x5B, 0x5F, 0x70, 0x7F, 0x7B]

    print("Ones place")
    for i in range(256):
        write(i, digits[i % 10])
    print("Tens place")
    for i in range(256):
        write(i + 256, digits[(i // 10) % 10])
    print("Hundreds place")
    for i in range(256):
        write(i + 512, digits[(i // 100) % 10])
    print("Sign place")
    for i in range(256):
        write(i + 768, 0)

    print("Ones place - two complement")
    for i in range(-128, 128):
        write((i & 0xFF)  + 1024, digits[abs(i) % 10])
    print("Tens place - two complement")
    for i in range(-128, 128):
        write((i & 0xFF)  + 1280, digits[(abs(i) // 10) % 10])
    print("Hundreds place -  two complement")
    for i in range(-128, 128):
        write((i & 0xFF)  + 1536, digits[(abs(i) // 100) % 10])
    print("Sign place - two complement")
    for i in range(-128, 128):
        if i < 0:
            write((i & 0xFF) + 1792, 0x01)
        else:
            write((i & 0xFF)  + 1792, 0x00)


def erase():
    for i in range(256):
        write(i, 0xFF)

#prog(0)
#multiplexed()
printContents()
#erase()


# ---🧹---#
GPIO.cleanup()
