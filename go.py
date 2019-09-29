#! /usr/bin/env python

import rospy
import time
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

def lasersc(msg):
    global min_las
    global mes
    min_las = min(msg.ranges)
    mes = msg.ranges

min_las = 1
cmd_vel = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
mes = []

rospy.init_node("laser_values")
sub = rospy.Subscriber('/scan', LaserScan, lasersc)
go_to = Twist()

def FullForward(sec):
    global go_to
    global cmd_vel
    t0 = time.time()
    go_to.linear.x = 1
    go_to.linear.y = 0
    go_to.linear.z = 0
    go_to.angular.x = 0
    go_to.angular.y = 0
    go_to.angular.z = 0
    cmd_vel.publish(go_to)
    if t0 > 0:
        while float(time.time() - t0) < sec:
            pass
        Stop()

def Stop():
    global go_to
    global cmd_vel
    go_to.linear.x = 0
    go_to.linear.y = 0
    go_to.linear.z = 0
    go_to.angular.x = 0
    go_to.angular.y = 0
    go_to.angular.z = 0
    cmd_vel.publish(go_to)

def Rotate(deg):
    global go_to
    global cmd_vel
    go_to.linear.x = 0
    go_to.linear.y = 0
    go_to.linear.z = 0
    go_to.angular.x = 0
    go_to.angular.y = 0
    if deg > 0:
        go_to.angular.z = 1
    else:
        go_to.angular.z = -1
        deg = -deg
    cmd_vel.publish(go_to)
    deg = float(deg)
    t = float(deg / 360 * 6.55) # 6.55 - time to rot. 360 deg (4 exp)
    time.sleep(t)

def FindMinDistLeft():
    global mes
    deg = 90
    dist_min = mes[90]
    for i in range(180):
        if mes[i] < dist_min:
            deg = i
            dist_min = mes[i]
    return [deg, dist_min]

def FindMinDistRight():
    global mes
    deg = 270
    dist_min = mes[deg]
    for i in range(180, 360):
        if mes[i] < dist_min:
            deg = i
            dist_min = mes[i]
    return [deg, dist_min]

time.sleep(0.4) # Delay to laser init

# --------------------------------------------------------- #

t0 = time.time()

SPEED = float(input("TURN SPEED: ")) / 100

Stop()

# step 1
start_deg = 0
while not rospy.is_shutdown():
    print("Step 1")
    deg, dist_min = FindMinDistRight()
    deg = float(deg)
    rot = deg - 270.0
    dist_min = float(dist_min)
    if dist_min > 0.2:
        rot -= 15
    if dist_min > 0.4:
        rot = rot * dist_min / 0.7
    if rot > 90:
        rot = 30
    elif rot < -90:
        rot = -30
    if rot > -5 and rot < 5:
        rot = 0
    if start_deg + rot <= -90:
        rot = -90 - start_deg
        Rotate(rot)
        print(start_deg)
        break
    start_deg += rot
    print(start_deg)
    if rot != 0:
        Rotate(rot)
    FullForward(SPEED)

# step2
start_deg = 0
while not rospy.is_shutdown():
    print("Step 2")
    deg, dist_min = FindMinDistLeft()
    deg = float(deg)
    dist_min = float(dist_min)
    rot = deg - 90.0
    if dist_min > 0.2:
        rot += 15
    if dist_min > 0.4:
        rot = rot * dist_min / 0.7
    if rot > 90:
        rot = 30
    elif rot < -90:
        rot = -30
    if rot > -5 and rot < 5:
        rot = 0
    if start_deg + rot >= 360:
        rot = 360 - start_deg
        Rotate(rot)
        print(start_deg)
        break
    start_deg += rot
    print(start_deg)
    if rot != 0:
        Rotate(rot)
    FullForward(SPEED)

# step3
start_deg = 0
while not rospy.is_shutdown():
    print("Step 3")
    deg, dist_min = FindMinDistRight()
    deg = float(deg)
    rot = deg - 270.0
    dist_min = float(dist_min)
    if dist_min > 0.2:
        rot -= 15
    if dist_min > 0.4:
        rot = rot * dist_min / 0.7
    if rot > 90:
        rot = 30
    elif rot < -90:
        rot = -30
    if rot > -5 and rot < 5:
        rot = 0
    if start_deg <= -270:
        rot = -270 - start_deg
        Rotate(rot)
        print(start_deg)
        break
    start_deg += rot
    print(start_deg)
    if rot != 0:
        Rotate(rot)
    FullForward(SPEED)

# --------------------------------------------------------- #
Stop()

print(time.time() - t0)
