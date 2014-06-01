#! /usr/bin/env python2.7

import RPi.GPIO as GPIO
from RPLCD import CharLCD, cleared, cursor
import time
import sys

# Auspex LCD for Warhammer 40,000 Victory Point and Turn Tracking
# https://github.com/miproductions/auspex

# Initialize display. All values have default values and are therefore optional.
lcd = CharLCD(pin_rs=15, pin_rw=18, pin_e=16, pins_data=[21, 22, 23, 24],
    numbering_mode=GPIO.BOARD, cols=20, rows=4, dotsize=8)

# define the aquila custom characters
aquila0 = (0b01111,0b00011,0b00001,0b00000,0b00000,0b00000,0b00000,0b00000)
lcd.create_char(0,aquila0)
aquila1 = (0b11101,0b11000,0b11111,0b11111,0b01101,0b00001,0b00011,0b00010)
lcd.create_char(1,aquila1)
aquila2 = (0b01011,0b10001,0b11111,0b11111,0b11011,0b11000,0b11100,0b10100)
lcd.create_char(2,aquila2)
aquila3 = (0b11111,0b11100,0b11000,0b10000,0b00000,0b00000,0b00000,0b00000)
lcd.create_char(3,aquila3)

def calc_indent(the_text):
    return int(round((20 - len(the_text)) / 2))

# Row definitions, centering indents and text
row_version = 0
row_version_txt = 'AUSPEX 420014.M2'
row_version_indent = calc_indent(row_version_txt)
row_msg = 1
row_msg_txt = ""
row_msg_indent = 0
row_met = 2
row_met_txt = ''
row_met_indent = 4
row_score = 3
row_score_txt = ''
row_score_indent = 3

# current cursor location for menus
# 0: undefined
# 1: P1 VP
# 2: Turn Count
# 3: P2 VP
menu_pos = 0

# turn definitions
turns = ['<T1<','>T1>','<T2<','>T2>','<T3<','>T3>','<T4<','>T4>','<T5<','>T5>','<T6<','>T6>','<T7<','>T7>','END']
turn_current = 0

# VP scores
score_p1 = 0
score_p2 = 0
str_vp = 'VP:'
str_sep = ' '

# init the mission clock
time_start = time.time()

# button pins (BOARD Rev 1 numbering)
# all should be set input pulled up
but_cycle = 26
but_incr = 12
but_decr = 7
GPIO.setup(but_cycle, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(but_incr, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(but_decr, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# prep the LCD
lcd.clear()
lcd.home()

# global abort state
abort = False

# global clear state
req_clear = False

# button event methods

def callback_cycle(channel):
    # function that moves the blinking cursor to indicate which value
    # will be incremented or decremented
    print "falling edge detected on cycle button pin " + str(but_cycle)
    # just for testing TODO remove
    global score_p1
    score_p1 += 1
    global req_clear
    req_clear = True

def callback_incr(channel):
    print "falling edge detected on increment button pin " + str(but_incr)

def callback_decr(channel):
    print "falling edge detected on decrement button pin " + str(but_decr)

def format_score():
    return str_vp + str(score_p1) + str_sep + turns[turn_current] + str_sep + str_vp + str(score_p2)

def format_met():
    return time.strftime("%H:%M:%S", time.gmtime(time.time() - time_start))

def refresh(do_clear):
    # refresh the display
    if (do_clear):
        lcd.clear()
        lcd.home()
        global req_clear
        req_clear = False
    # version on row 0
    with cursor(lcd, row_version,row_version_indent):
        lcd.write_string(row_version_txt)
    if (row_msg_txt == ""):
        # no message, just display the Aquila on row 1
        with cursor(lcd, row_msg, 8):
            lcd.write_string(unichr(0))
            lcd.write_string(unichr(1))
            lcd.write_string(unichr(2))
            lcd.write_string(unichr(3))
    else:
        # we have a message, display that instead
        with cursor(lcd, row_msg, calc_indent(row_msg_txt)):
            lcd.write_string(row_msg_txt)
        
    # MET on row 2
    with cursor(lcd,row_met,row_met_indent):
        lcd.write_string('MET ' + format_met())
    # score on row 3
    with cursor(lcd,row_score,row_score_indent):
        lcd.write_string(format_score())

# register events
GPIO.add_event_detect(but_cycle, GPIO.FALLING, callback=callback_cycle, bouncetime=200)
GPIO.add_event_detect(but_incr, GPIO.FALLING, callback=callback_incr, bouncetime=200)
GPIO.add_event_detect(but_decr, GPIO.FALLING, callback=callback_decr, bouncetime=200)

# beginning of main loop
print row_version_txt + " STARTED"
try:
    refresh(True)
    while not abort:
        refresh(req_clear)
        time.sleep(1)
        # print "tick.."
        
except KeyboardInterrupt:
    print "interrupted by user, exiting"
except:
    print "unhandled Exception, exiting: ", sys.exc_info()[0]
finally:
    # exit gracefully with useful info
    print row_version_txt + " TERMINATED"
    print "MET: " + format_met()
    print "SCORE: " + format_score()
    lcd.close(clear=True)
    
