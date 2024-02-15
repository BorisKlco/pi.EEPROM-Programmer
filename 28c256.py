import RPi.GPIO as GPIO
import time

ADDR_PIN = [26,20,19,1,25,12,16,13,6,5,11,9,10,27,22]
EEPROM_SIZE = len(ADDR_PIN)
# -------
DATA_PIN = [23,18,15,14,8,3,4,17]
# -------
WE = 21
OE = 7
CE = 24
# -------
GPIO.setmode(GPIO.BCM)
GPIO.setup(CE, GPIO.OUT)
GPIO.output(CE, 0)
time.sleep(0.1)


def setAddress(addr):
    result = []
    for i in range(EEPROM_SIZE):
        result.append(1 if (addr & (1 << (EEPROM_SIZE - 1 - i))) != 0 else 0)
    return result


def setData(data):
    result = []
    for i in range(8):
        result.append(1 if (data & (1 << (7 - i))) != 0 else 0)
    return result

def read(addr):
    GPIO.setup((WE, OE), GPIO.OUT)
    GPIO.output(WE, 1)
    GPIO.output(OE, 0)
    time.sleep(0.001)
    BYTE_ADDR = setAddress(addr)
    BYTE_DATA = []

    for i, pin in enumerate(ADDR_PIN):
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, BYTE_ADDR[i])


    for pin in DATA_PIN:
        GPIO.setup(pin, GPIO.IN)

    for pin in DATA_PIN:
        BYTE_DATA.append(GPIO.input(pin))

    time.sleep(0.01)

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

    GPIO.output(WE, 0)
    time.sleep(0.01)
    GPIO.output(WE, 1)
    time.sleep(0.01)

# --------May the Force be with you------#
# ---- Ben Eater Our Lord and Savior 🙏--#
def printContents():
    for base in range(0, 64, 16):
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
    time.sleep(0.01)


# --------May the Force be with you------#
# ---- Ben Eater Our Lord and Savior 🙏--#

def erase():
    for i in range(0,64):
        write(i, 0x55)

#erase()

time.sleep(0.1)
printContents()
# ---🧹---#
GPIO.cleanup()
time.sleep(0.1)
