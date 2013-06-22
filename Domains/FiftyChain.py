#Copyright (c) 2013, Alborz Geramifard, Robert H. Klein, and Jonathan P. How
#All rights reserved.

#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

#Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

#Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

#Neither the name of ACL nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#Locate RLPy
#================
import sys, os
RL_PYTHON_ROOT = '.'
while os.path.abspath(RL_PYTHON_ROOT) != os.path.abspath(RL_PYTHON_ROOT + '/..') and not os.path.exists(RL_PYTHON_ROOT+'/RLPy/Tools'):
    RL_PYTHON_ROOT = RL_PYTHON_ROOT + '/..'
if not os.path.exists(RL_PYTHON_ROOT+'/RLPy/Tools'):
    print 'Error: Could not locate RLPy directory.' 
    print 'Please make sure the package directory is named RLPy.'
    print 'If the problem persists, please download the package from http://acl.mit.edu/RLPy and reinstall.'
    sys.exit(1)
RL_PYTHON_ROOT = os.path.abspath(RL_PYTHON_ROOT + '/RLPy')
sys.path.insert(0, RL_PYTHON_ROOT)

from Tools import *
from Domain import *
######################################################
# \author Alborz Geramifard, Robert H. Klein at MIT, Dec. 21, 2012
######################################################
# 50-state chain described by Lagoudakis & Parr, 2003 \n
# s0 <-> s1 <-> ... <-> s50   \n
# Actions are left [0] and right [1]
# Reward of +1 at states 10 and 41 (indices 0 and 9) \n
# Actions succeed with probability .9, otherwise execute opposite action.
######################################################
class FiftyChain(Domain):
    GOAL_REWARD = 1
	## Indices of states with rewards
    GOAL_STATES = [9,40] 
	## Set by the domain = min(100,rows*cols)
    episodeCap  = 50            
	## Used for graphical normalization
    MAX_RETURN  = 2.5
	## Used for graphical normalization
    MIN_RETURN  = 0  	
	## Used for graphical shifting of arrows
    SHIFT       = .01            
	## Used for graphical radius of states
    RADIUS      = .05
	## Stores the graphical pathes for states so that we can later change their colors 
    circles     = None
	## Number of states in the chain
    chainSize   = 50
	## Y values used for drawing circles
    Y           = 1             
    actions_num = 2
	## Probability of taking the other (unselected) action
    p_action_failure = 0.1      
    V_star      = [0.25424059953210576, 0.32237043339365301, 0.41732244995544071, 0.53798770416976416, 0.69467264588670452, 0.91307612341516964, 1.1996067857970858, 1.5914978718669359, 2.1011316163482885, 2.7509878207260079, 2.2007902565808002, 1.7606322052646419, 1.4085057642117096, 1.1268046113693631, 0.90144368909548567, 0.72115495127639073, 0.5769239610211111, 0.46153916881688833, 0.36923133505350991, 0.29538506804280829, 0.23630805443424513, 0.18904644354739669, 0.15123715483791522, 0.12098972387033219, 0.096791779096267572, 0.077433423277011526, 0.064110827579671889, 0.080577201155275072, 0.10271844729124571, 0.13354008685155827, 0.17749076168535796, 0.22641620289304287, 0.29916005826456937, 0.39326998437016564, 0.52325275246999614, 0.67438770340963006, 0.90293435616054674, 1.1704408409975584, 1.5213965403184493, 2.0462009513290296, 2.7423074964894685, 2.1938459971915725, 1.7550767977532584, 1.404061438202612, 1.1232491505620894, 0.89859932044966939, 0.71887945635973116, 0.57510356508778659, 0.46008285207022837, 0.36806628165617972]          # Array of optimal values at each state
    
	# The optimal policy for this domain
    optimalPolicy = None        
	# Should the domain only allow optimal actions
    using_optimal_policy = False 
    
    #Plotting values
    domain_fig          = None
    value_function_fig  = None
    policy_fig          = None
    V_star_line         = None
    V_approx_line       = None
    COLORS              = ['g','k']
    LEFT = 0
    RIGHT = 1
    
    #Constants in the map
    def __init__(self,logger = None):
        self.start              = 0
        self.statespace_limits  = array([[0,self.chainSize-1]])
        super(FiftyChain,self).__init__(logger)
        self.optimal_policy = array( [-1 for dummy in range(0, self.chainSize)]) # To catch errors
        self.storeOptimalPolicy()
        self.gamma = 0.8 # Set gamma to be 0.8 for this domain per L & P 2007
    def storeOptimalPolicy(self):
        self.optimal_policy[arange(self.GOAL_STATES[0])] = self.RIGHT            
        goalStateIndices = arange(1,len(self.GOAL_STATES))
        for i in goalStateIndices:
            goalState1 = self.GOAL_STATES[i-1]
            goalState2 = self.GOAL_STATES[i]
            averageState = int(mean([goalState1, goalState2]))
            self.optimal_policy[arange(goalState1, averageState)] = self.LEFT
            self.optimal_policy[arange(averageState, goalState2)] = self.RIGHT
        self.optimal_policy[arange(self.GOAL_STATES[-1], self.chainSize)] = self.LEFT
    def showDomain(self,s,a = 0):
        #Draw the environment
        if self.circles is None:
           self.domain_fig = pl.subplot(3,1,1)
           pl.figure(1, (self.chainSize*2/10.0, 2))
           self.domain_fig.set_xlim(0, self.chainSize*2/10.0)
           self.domain_fig.set_ylim(0, 2)
           self.domain_fig.add_patch(mpatches.Circle((1/5.0+2/10.0*(self.chainSize-1), self.Y), self.RADIUS*1.1, fc="w")) #Make the last one double circle
           self.domain_fig.xaxis.set_visible(False)
           self.domain_fig.yaxis.set_visible(False)
           self.circles = [mpatches.Circle((1/5.0+2/10.0*i, self.Y), self.RADIUS, fc="w") for i in range(self.chainSize)]
           for i in range(self.chainSize):
               self.domain_fig.add_patch(self.circles[i])
               pl.show()
            
        [p.set_facecolor('w') for p in self.circles]
        [self.circles[p].set_facecolor('g') for p in self.GOAL_STATES]
        self.circles[s].set_facecolor('k')
        pl.draw()
    def showLearning(self, representation):
        allStates = arange(0,self.chainSize)
        X   = arange(self.chainSize)*2.0/10.0-self.SHIFT
        Y   = ones(self.chainSize) * self.Y
        DY  = zeros(self.chainSize)  
        DX  = zeros(self.chainSize)
        C   = zeros(self.chainSize)

        if self.value_function_fig is None:
            self.value_function_fig = pl.subplot(3,1,2)
            self.V_star_line = self.value_function_fig.plot(allStates,self.V_star)
            V   = [representation.V(s) for s in allStates]
            
            # Note the comma below, since a tuple of line objects is returned
            self.V_approx_line, = self.value_function_fig.plot(allStates, V, 'r-',linewidth = 3)
            self.V_star_line    = self.value_function_fig.plot(allStates, self.V_star, 'b--',linewidth = 3)
            pl.ylim([0, self.GOAL_REWARD * (len(self.GOAL_STATES)+1)]) # Maximum value function is sum of all possible rewards
            
            self.policy_fig = pl.subplot(3,1,3)
            self.policy_fig.set_xlim(0, self.chainSize*2/10.0)
            self.policy_fig.set_ylim(0, 2)
            self.arrows = pl.quiver(X,Y,DX,DY, C, cmap = 'fiftyChainActions', units='x', width=0.05,scale=.008, alpha= .8 )#headwidth=.05, headlength = .03, headaxislength = .02)
            self.policy_fig.xaxis.set_visible(False)
            self.policy_fig.yaxis.set_visible(False)
        
        V   = [representation.V(s) for s in allStates]
        pi  = [representation.bestAction(s) for s in allStates]
        #pi  = [self.optimal_policy[s] for s in allStates]
        
        DX  = [(2*a-1)*self.SHIFT*.1 for a in pi]
        
        self.V_approx_line.set_ydata(V)
        self.arrows.set_UVC(DX,DY,pi)
        pl.draw()
    def step(self,s,a):
        actionFailure = (random.random() < self.p_action_failure)
        if a == self.LEFT or (a == self.RIGHT and actionFailure): #left
            ns = max(0,s-1)
        elif a == self.RIGHT or (a == self.LEFT and actionFailure):
            ns = min(self.chainSize-1,s+1)
        terminal = self.isTerminal(ns)
        r = self.GOAL_REWARD if s in self.GOAL_STATES else 0
        return r,ns,terminal
    def s0(self):
        return random.randint(0,self.chainSize)
    def isTerminal(self,s):
        return False # s == [[]]
    def possibleActions(self,s):
        if self.using_optimal_policy: return array([self.optimal_policy[s]])
        else: return arange(self.actions_num)
    def L_inf_distance_to_V_star(self, representation):
            V   = array([representation.V(s) for s in arange(self.chainSize)])
            return linalg.norm(V-self.V_star,inf) 

if __name__ == '__main__':
    p = FiftyChain();
    p.test(1000)
    
    