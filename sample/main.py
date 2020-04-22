"""
TODO::
Low Voltage Detection (LVD)
Waterproof
TURN LIMIT BASED ON MOTOR SIZE
braking control
Thermal shutdown protection
Easy installation in Traxxas models 

Gradually increase motor speed
Gradually decrease motor speed
"reverse slam" protection (creates feedback in circuit)

Figure out power for servo / receiver
(currently using USB from a seperate USB port on the same battery
2.4/2 = 1.2 amps with each USB cable, unsure if one side is able
to draw more current while decreasing the other side/port.)
"""

import sys, time, pigpio
import piconzero as pz
last = [None]*32
cb = []

#set the pi we are workign with (default to local)
pi = pigpio.pi()

#let test this, subject to change, useful for adjusting RPM.
speed = 25

#reference point to poll for changes
futureTick = 20001

#pin row on piconzero
turnServo = 0
pz.init()

# Set output mode to Servo and frequency for servo
pz.setOutputConfig(turnServo, 2)
pi.set_PWM_frequency(18,240)

# Set frequency for Motor 50Hz * 25 speed = 1250RPM
#20.83_ rotations per second
pi.set_PWM_frequency(4,50)

#max right
panMax=180
#center pos
panCenter=90
#max left
panMin=0

#initially center panned, using this for PWM smooth transitions
panValue = 90
pz.setOutput (turnServo, panCenter)

#set radius of turns on tx "pressure"
heavyPan=18
mediumPan=9
lightPan=5

#how quickly do we adjust the servo? 20000us = 200ms
#increase for smoother reactions decrease for more sharpness
panDelay=15000

#int, int, string <-- needs to be bit/int eventually
def checkTick(nowTick = 0, pan = None, weight = 10):
   global futureTick
   #for servo
   global panValue
   #for motor
   global speed
#not even error checking yet
   if nowTick >= futureTick + panDelay:
#then check pan, possibilities are L,R,C (Left, Right, Center) (todo: change to bits)
#!! switch statement is faster also...
      if pan == "L":
         if panValue - weight >= panMin:
            print("LEFT@"+str(weight)+":"+str(panValue)+"\n")
            panValue -= weight
            pz.setOutput(turnServo, panValue - weight)
      elif pan == "R":
         if panValue + weight <= panMax:
            print("RIGHT@"+str(weight)+":"+str(panValue)+"\n")
            panValue += weight
            pz.setOutput(turnServo, panValue + weight)
      elif pan == "C":
         if panValue > panCenter:
            print("CENTERING FROM RIGHT@"+str(weight)+":"+str(panValue)+"\n")
            panValue = 90
            pz.setOutput(turnServo, panValue - weight)
         elif panValue < panCenter:
            print("CENTERING FROM LEFT@"+str(weight)+":"+str(panValue)+"\n")
            panValue = 90
            pz.setOutput(turnServo, panValue + weight)
        # else:
         #   print("CENTERED")
      if pan == "F":
         print("FORWARD")
         #pz.forward(weight)
      elif pan == "B":
         print("REVERSE")
         #pz.reverse(weight)

      futureTick = nowTick + panDelay
      
def cbf(GPIO, level, tick):
   if last[GPIO] is not None:
      diff = pigpio.tickDiff(last[GPIO], tick)
      #print("G={} l={} d={}".format(GPIO, level, diff))

      if GPIO == 18:
         #Heavy Center
         if 1490 <= diff <= 1510:
            checkTick(tick, "C", 1)

         #310 difference between center and right
         #Heavy Right
         elif 990 <= diff <= 1010:
            checkTick(tick, "R", heavyPan)
         #Medium Right
         elif 1009 <= diff <= 1299:
            checkTick(tick, "R", mediumPan)
         #Light Right
         elif 1300 <= diff <= 1420:
            checkTick(tick, "R", lightPan)

         #Heavy Left
         elif 1960 <= diff <= 1980:
            checkTick(tick, "L", heavyPan)
         #Medium Left
         elif 1760 <= diff <= 1979:
            checkTick(tick, "L", mediumPan)
         #Light Left
         elif 1660 <= diff <= 1759:
            checkTick(tick, "L", lightPan)

      if GPIO == 4:
         #print("GPIO4: "+str(diff)+"\n")

         #if 8378 <= diff <= 8385:
            #print("NEUTRAL")
         #neutral::
         #1485-1490
         #8378-8385

         #493 difference between N and F
         if 7878 <= diff <= 7885:
            checkTick(tick, "F", speed)
         #forward::
         #1980-1985
         #7878-7885

         #494 difference between N and R
         elif 8879 <= diff <= 8885:
            checkTick(tick, "B", speed)
         #reverse::
         #984-991
         #8879-8885

   last[GPIO] = tick

if not pi.connected:
   exit()

if len(sys.argv) == 1:
   G = range(0, 32)
else:
   G = []
   for a in sys.argv[1:]:
      G.append(int(a))

for g in G:
   cb.append(pi.callback(g, pigpio.EITHER_EDGE, cbf))

try:
   while True:
      time.sleep(60)
except KeyboardInterrupt:
   print("\nTidying up")
   pz.cleanup()
   for c in cb:
      c.cancel()

pi.stop()