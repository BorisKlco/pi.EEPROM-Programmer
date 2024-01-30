import wiringpi
import inquirer
import sys
import time

###
INPUT = 0
OUTPUT = 1
CUSTOM_DATA = []

##EEPROM
# Active Low 👇
E_WE = 30
E_OE = 21
E_DATA = [6, 10, 11, 31, 26, 27, 28, 29]

## Shift Register
# Data in
S_DATA = 12
# Storage
S_RCLK = 13
# Clock
S_SRCLK = 14


def setAddr(addr, enableOutput):
    ##Set OE on EEPROM - Active Low
    wiringpi.digitalWrite(E_OE, enableOutput)
    ##Shift data - Data, Clock, MSBFIRST, ADDR
    wiringpi.shiftOut(S_DATA, S_SRCLK, 1, (addr >> 8))
    wiringpi.shiftOut(S_DATA, S_SRCLK, 1, (addr & 255))
    ##Save data to storage  register
    wiringpi.digitalWrite(S_RCLK, 0)
    wiringpi.digitalWrite(S_RCLK, 1)
    wiringpi.digitalWrite(S_RCLK, 0)


def read(addr):
    setAddr(addr, 0)
    for pin in E_DATA:
        wiringpi.pinMode(pin, INPUT)
    data = 0
    for pin in reversed(E_DATA):
        data = (data << 1) + wiringpi.digitalRead(pin)
    time.sleep(0.01)
    return data


def write(addr, data):
    setAddr(addr, 1)
    for pin in E_DATA:
        wiringpi.pinMode(pin, OUTPUT)
    for pin in E_DATA:
        wiringpi.digitalWrite(pin, data & 1)
        data = data >> 1

    wiringpi.digitalWrite(E_WE, 0)
    time.sleep(0.001)
    wiringpi.digitalWrite(E_WE, 1)
    time.sleep(0.01)


def printEE(sectors=1):
    for sector in range(sectors):
        from_sector = 256 * sector
        to_sector = 256 * (sector + 1)
        print("Sector:", from_sector, "to", to_sector)
        for base in range(256 * sector, 256 * (sector + 1), 16):
            data = [0] * 16
            for offset in range(16):
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


def ask_instructions():
    begin_instructions = [
        inquirer.List(
            "begin",
            message="EEPROM Programmer",
            choices=["Read", "Write", "Erase", "Quit"],
        ),
    ]
    instructions = inquirer.prompt(begin_instructions)

    match instructions["begin"]:
        case "Read":
            ask_read_instructions()
        case "Write":
            ask_write_instructions()
        case "Erase":
            print("Erasing...")
            for addr in range(2048):
                write(addr, 0xFF)
            print("done...")
        case "Quit":
            sys.exit("\nBye!")


def ask_read_instructions():
    picking_read = [
        inquirer.List(
            "picking_read",
            message="Reading",
            choices=["Read address", "Read sector", "Read All", "Back"],
        ),
    ]

    asking_addr = [inquirer.Text("addr", message="What address?")]
    asking_sectors = [
        inquirer.Text("sectors", message="How many sectors of 256? (8 is 2048)")
    ]
    read_instructions = inquirer.prompt(picking_read)

    match read_instructions["picking_read"]:
        case "Read address":
            read_addr_answer = inquirer.prompt(asking_addr)
            print(
                "Data for",
                read_addr_answer["addr"],
                "-",
                read(read_addr_answer["addr"]),
            )
            print("done...")
        case "Read sector":
            read_sector_answer = inquirer.prompt(asking_sectors)
            printEE(read_sector_answer["sectors"])
            print("done...")
        case "Read All":
            print("Reading EEPROM....")
            printEE(8)
            print("done...")
        case "Back":
            ask_instructions()


def ask_write_instructions():
    picking_write = [
        inquirer.List(
            "picking_write",
            message="Writing",
            choices=["Predefine data", "Write custom data", "Back"],
        ),
    ]

    asking_to_write = [
        inquirer.Text("addr", message="What address?"),
        inquirer.Text("data", message="What data?"),
    ]
    write_instructions = inquirer.prompt(picking_write)

    match write_instructions["picking_write"]:
        case "Predefine data":
            print("Writing predefine data...")
            for addr, data in enumerate(CUSTOM_DATA):
                write(addr, data)
            print("done...")
        case "Write custom data":
            write_answer = inquirer.prompt(asking_to_write)
            print("Writing to", write_answer["addr"], "data", write_answer["data"])
            write(write_answer["addr"], write_answer["data"])
            print("done...")
        case "Back":
            ask_instructions()


def init():
    wiringpi.wiringPiSetup()
    wiringpi.digitalWrite(S_DATA, OUTPUT)
    wiringpi.digitalWrite(S_SRCLK, OUTPUT)
    wiringpi.digitalWrite(S_RCLK, OUTPUT)

    wiringpi.digitalWrite(E_WE, 1)
    wiringpi.digitalWrite(E_WE, OUTPUT)

    ask_instructions()


init()
