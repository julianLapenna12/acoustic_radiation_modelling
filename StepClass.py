	#!/usr/bin/env python3 
	#
# NOTE - Only for use on Raspberry Pi or other SBC.
#

import time
import configparser
import atexit
import board
import RPi.GPIO as GPIO
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper

class twostep:
    def __init__(self, confname='UNDEFINED', stop_at_exit=False):
        """

      """
        self.confname = confname
        
        self.m_delay = 0.001        
        #Open config file and read config data
        self.config = configparser.ConfigParser()
        self.config.read('/home/public/stepconfig.ini')
        
        self.mpos = int(self.config[confname]['CurrentSteps'])        
        
        self.maxspeed = int(self.config[confname]['MaxSpeed'])
                
        self.minlimit = int(self.config[confname]['MinLimit'])
                
        self.maxlimit = int(self.config[confname]['MaxLimit'])        
        
        self.stepmult = int(self.config[confname]['StepMultiplier'])
        
        #Check if it's an adafruit or GPIO motor
        try:
            self.i2caddr = int(self.config[confname]['i2caddr'])
        
            self.adaport = int(self.config[confname]['adaport'])
            
            self.kit = MotorKit(steppers_microsteps=4, address=self.i2caddr)
        except KeyError: #GPIO motor
            
            self.i2caddr = -1
            self.adaport = -1
            
            self.stepgpio = int(self.config[confname]['stepgpio'])
            self.dirgpio = int(self.config[confname]['dirgpio'])
            
            GPIO.setmode(GPIO.BCM)
            
            GPIO.setup(self.stepgpio, GPIO.OUT)
            GPIO.setup(self.dirgpio, GPIO.OUT)
            GPIO.output(self.stepgpio, GPIO.LOW)
            GPIO.output(self.dirgpio, GPIO.LOW)
            
        
        if stop_at_exit:
            atexit.register(self.stop)

    def _m_speed(self, speed):
        #Set the speed of motor 1, in steps/sec approx
        #Check speed limits
        if speed < 0:
            speed = 1
            print("Using minimum speed of 1")
        elif speed > self.maxspeed:
            speed = self.maxspeed
            print("Using maximum speed of " + str(self.maxspeed))
            
            
        self.m_delay = 1/(speed * self.stepmult)        

    def stop(self):
        """Release motors"""
        if self.adaport == 1:
            self.kit.stepper1.release()
        elif self.adaport == 2:
            self.kit.stepper2.release()

    def move(self, steps, speed = 1):
        """
        """
        # Set motor speed
        self._m_speed(speed)
        print("delay: ",self.m_delay)
        
        #Check position limits
        if self.mpos + steps >= self.maxlimit:
            steps = self.maxlimit - self.mpos
            print("Going to max limit " + str(self.maxlimit))
        elif self.mpos + steps <= self.minlimit:
            steps = self.minlimit - self.mpos
            print("Going to min limit " + str(self.minlimit))
            
        #Move forward
        if steps >= 1:
            if self.adaport == -1:
                GPIO.output(self.dirgpio, GPIO.HIGH)
                time.sleep(0.001)            
            try:
                for i in range(steps * self.stepmult):
                    self._step(direction = 'FORWARD')
                #print("Completed " + str(i))        
            
            #always stop at stepmult if interrupted            
            except:
                while((i + 1) % self.stepmult != 0):
                    self._step(direction = 'FORWARD')
                    i += 1
                print("Interrupted")
                steps = int((i + 1) / self.stepmult)
        
        #Move backward        
        if steps < 0:
            if self.adaport == -1:
                GPIO.output(self.dirgpio, GPIO.LOW)
                time.sleep(0.001)  
            try:
                for i in range(abs(steps * self.stepmult)):
                    self._step(direction = 'BACKWARD')                     
                    
            #always stop at stepmult if interrupted            
            except:
                while((i + 1) % self.stepmult != 0):
                    self._step(direction = 'BACKWARD')                                              
                    i += 1
                print("Interrupted")
                steps = int(((i + 1) / self.stepmult) * -1)
        
        #update step position
        self.mpos += steps
        #Read, modify, write step config file with new step position
        self.config.read('/home/public/stepconfig.ini')
        self.config[self.confname]['CurrentSteps'] = str(self.mpos)
        conf = open('/home/public/stepconfig.ini', 'w')
        self.config.write(conf)
        conf.close()
        
    def _step(self, direction = 'FORWARD'):
        if direction == 'FORWARD':
            if self.adaport == 1:
                self.kit.stepper1.onestep(direction=stepper.FORWARD, style=stepper.MICROSTEP)
                time.sleep(self.m_delay)
            elif self.adaport == 2:
                self.kit.stepper2.onestep(direction=stepper.FORWARD, style=stepper.MICROSTEP)
                time.sleep(self.m_delay)
            elif self.adaport == -1:
                GPIO.output(self.stepgpio, GPIO.HIGH)
                time.sleep(self.m_delay / 2.0)
                GPIO.output(self.stepgpio, GPIO.LOW)
                time.sleep(self.m_delay / 2.0)
        elif direction == 'BACKWARD':
            if self.adaport == 1:
                self.kit.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.MICROSTEP)
                time.sleep(self.m_delay)
            elif self.adaport == 2:
                self.kit.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.MICROSTEP)
                time.sleep(self.m_delay)
            elif self.adaport == -1:
                GPIO.output(self.stepgpio, GPIO.HIGH)
                time.sleep(self.m_delay / 2.0)
                GPIO.output(self.stepgpio, GPIO.LOW)
                time.sleep(self.m_delay / 2.0)           
        
            
