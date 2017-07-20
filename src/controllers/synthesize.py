import logging
from tulip import transys, spec, synth

# Create the system
sys = transys.FTS()
sys.states.add_from(['X0','X1','X2','X3','X4'])
sys.states.initial.add('X0')

# Define transitions
sys.transitions.add_comb({'X0'},{'X1'})
sys.transitions.add_comb({'X1'},{'X2','X0'})
sys.transitions.add_comb({'X2'},{'X3','X1'})
sys.transitions.add_comb({'X3'},{'X4','X2'})
sys.transitions.add_comb({'X4'},{'X3'})

# Couple states with atomic propositions
#sys.atomic_propositions.add_from({'X0','X1','X2','X3','X4'})
sys.atomic_propositions.add_from({'X0','X4'})
sys.states.add('X0',ap={'X0'})
#sys.states.add('X1',ap={'X1'})
#sys.states.add('X2',ap={'X2'})
#sys.states.add('X3',ap={'X3'})
sys.states.add('X4',ap={'X4'})

# Environment description
env_vars={'GoHome'}
env_init=set()
env_prog={'!GoHome'}
env_safe=set()

# System description
sys_vars={'X0reach'}
sys_init={'X0reach'}
sys_prog={'X4'}
sys_safe={'(X (X0reach) <-> X0) || (X0reach && !GoHome)'}
sys_prog |= {'X0reach'}
# Create the specification
specs = spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                    env_safe, sys_safe, env_prog, sys_prog)
specs.moore=False
specs.qinit = '\E \A'
ctrl = synth.synthesize('omega', specs, sys=sys)
assert ctrl is not None, 'unrealizable'

if not ctrl.save('discrete.png'):
    print(ctrl)
#
#
#
#
#
#

import numpy as np
import rospy
from ackermann_msgs.msg import AckermannDrive
from gazebo_msgs.msg import ModelStates

x=0

def getPos(data):
    global x
    x=data.pose[1].position.x-0.17

def findNext(curr):
    print curr
    if str(curr) is 'Sinit':
        next=0
        return next, 'X0'
    else:
        for prev,next,dct in ctrl.transitions(data=True):
            if (int(prev) is int(curr)) and ((dct['GoHome']) is (False)):
                print dct['loc']
                return str(next), dct['loc']
            elif (int(prev) is int(curr)) and ((dct['GoHome']) is (True)):
                print dct['loc']
                return str(next), dct['loc']

A = 0
B = 0.1
num_steps = 100
Q=2.
R=1.
N=1.
#P=np.zeros(num_steps)
#P[:]=Q
#for i in range(1,num_steps+1):
    #P[numsteps-i]=A*P[numsteps-i+1]*A-(A*P[numsteps-i+1]*B+N)*(R+B*P[numsteps-i+1]*B)**(-1)*(B*P[numsteps-i+1]*A+N)+Q
P=Q
F=(R+B*P*B)**(-1)*(B*P*A+N)
currState='Sinit'
GoHome=False
rospy.init_node('lqr')
rat=rospy.Rate(10)

rospy.Subscriber('gazebo/model_states',ModelStates,getPos)
pub=rospy.Publisher('ackermann_cmd',AckermannDrive,queue_size=10)
msg=AckermannDrive()
while not rospy.is_shutdown():
    currState, loc = findNext(currState)
    print loc[1]
    r = float(loc[1])+1
    print 'r ' + str(r)
    while (x-r)**2>0.01**2:
        print 'x ' + str(x)
        u=F*(r-x)
        msg.speed=u
        pub.publish(msg)
        rat.sleep()
    if (x-5)**2<0.01:
        msg.speed=0
        pub.publish(msg)
        exit()
msg.speed=0
pub.publish(msg)

