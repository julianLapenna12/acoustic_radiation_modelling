#!/usr/bin/env python3 
import configparser
import time
import fcntl
import os
import sys
import StepClass

#28BYJ-48 (at least our version) has 2048 steps per rev, with /4 microstep = 8192
#with default stepmultplier 16 this becomes 512 steps/rev

#Create and open a temporary file to prevent multiple instances of script
lock_file_pointer = os.open(f"/home/public/instance_stepper.lock", os.O_WRONLY | os.O_CREAT)
fcntl.lockf(lock_file_pointer, fcntl.LOCK_EX | fcntl.LOCK_NB)

config = configparser.ConfigParser()
config.read('/home/public/stepconfig.ini')

#Read number of motors from config
nummotors = int(config['GENERAL']['NumMotors'])
print("Using " + str(nummotors) + " motors")

motorlist = []

for i in range(nummotors):
    print("Motor " + str(i+1) + " alias: " + config['MOTOR' + str(i+1)]['Alias'])
    motorlist.append(StepClass.twostep(confname = ('MOTOR' + str(i+1))))

for i in range(nummotors):
    print("Current motor " + str(i+1) + " position: " + config['MOTOR' + str(i+1)]['CurrentSteps'])
    print("Moving motor " + str(i+1) + " to default position: " + config['MOTOR' + str(i+1)]['DefaultSteps'])
    motorlist[i].move(int(config['MOTOR' + str(i+1)]['DefaultSteps']) - int(config['MOTOR' + str(i+1)]['CurrentSteps']), int(config['MOTOR' + str(i+1)]['MaxSpeed']))

print("Done!")