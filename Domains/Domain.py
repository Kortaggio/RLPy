#Copyright (c) 2013, Alborz Geramifard, Robert H. Klein, and Jonathan P. How
#All rights reserved.

#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

#Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

#Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

#Neither the name of ACL nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

## \file Domain.py
######################################################
# \author Developed by Alborz Geramiard Oct 25th 2012 at MIT
######################################################

from Tools import *
from pydoc import classname

## The Domain controls the environment in which the \ref Agents.Agent.Agent "Agent" resides and the goal that said Agent is trying to acheive.
#
# The Agent interacts with the %Domain in discrete timesteps called 'episodes'. Each episode, the %Domain provides the Agent with some observations
# about its surroundings. Based on that information, the Agent informs the %Domain what action it wants to perform.
# The %Domain then calculates the effects this action has on the environment and returns the new state, a reward/penalty, and whether or not the episode is over or not (thus resetting the agent to its initial state).
# This process repeats until the %Domain determines that the Agent has either completed its goal or
# failed. The \ref Experiments.Experiment.Experiment "Experiment" controls this cycle.
#
# Because Agents are designed to be agnostic to the %Domain that they are acting within and the problem they are trying to solve,
# the %Domain needs to completely describe everything related to the task. Therefore, the %Domain must not only define the observations
# that the Agent receives, but also the states it can be in, the actions that it can perform, and the relationships between the three.
# Note that because RL-Agents are designed around obtaining a reward, observations that the %Domain returns should include a reward.
#
# The \c %Domain class is a superclass that provides the basic framework for all Domains. It provides the methods and attributes
# that allow child classes to interact with the \c %Agent and \c Experiment classes within the RLPy library.
# %Domains should also provide methods that provide visualization of the %Domain itself and of the Agent's learning (showDomain and showLearning)   \n
# All new domain implementations should inherit from \c %Domain.
#
# \note Though the state s can take on almost any
# value, if a dimension is not marked as 'continuous'
# then it is assumed to be integer.

class Domain(object):
	## The discount factor by which rewards are reduced
    gamma = .9
	## The number of possible states in the domain
    states_num = 0 # was None
	## The number of Actions the agent can perform
    actions_num = 0 # was None
	## Limits of each dimension of the state space. Each row corresponds to one dimension and has two elements [min, max]
    statespace_limits = [] # was None
	## Limits of each dimension of a discrete state space. This is the same as statespace_limits, without the extra -.5, +.5 added to each dimension
    discrete_statespace_limits = [] # was None
	## Number of dimensions of the state space
    state_space_dims = 0 # was None
	## List of the continuous dimensions of the domain
    continuous_dims = []
	## The cap used to bound each episode (return to state 0 after)
    episodeCap = None
	## A simple object that records the prints in a file
    logger = None
    ## Termination Signal of Episode: episode is not over
    NOT_TERMINATED          = 0
	## Termination Signal of Episode: episode is over, neither goal or fail state reached
    NOMINAL_TERMINATION     = 1
	## Termination Signal of Episode: episode is over, goal or fail state reached
    CRITICAL_TERMINATION    = 2

    ## some domains may have a hidden state which is saved in this variable
    hidden_state_ = None

	## Initializes the \c %Domain object. See code
	# \ref Domain_init "Here".

	# [init code]
    def __init__(self,logger):
        self.logger = logger
        for v in ['statespace_limits','actions_num','episodeCap']:
            if getattr(self,v) == None:
                raise Exception('Missed domain initialization of '+ v)
        self.state_space_dims = len(self.statespace_limits)
        self.gamma = self.gamma * 1.0 # To make sure type of gamma is float. This will later on be used in LSPI to force A matrix to be float
        # For discrete domains, limits should be extended by half on each side so that the mapping becomes identical with continuous states
        # The original limits will be saved in self.discrete_statespace_limits
        self.extendDiscreteDimensions()
        if self.continuous_dims == []:
            self.states_num = int(prod(self.statespace_limits[:,1]-self.statespace_limits[:,0]))
        else:
            self.states_num = inf
        if logger:
            self.logger.line()
            self.logger.log("Domain:\t\t"+str(className(self)))
            self.logger.log("Dimensions:\t"+str(self.state_space_dims))
            self.logger.log("|S|:\t\t"+str(self.states_num))
            self.logger.log("|A|:\t\t"+str(self.actions_num))
            self.logger.log("|S|x|A|:\t\t"+str(self.actions_num*self.states_num))
            self.logger.log("Episode Cap:\t"+str(self.episodeCap))
            self.logger.log("Gamma:\t\t"+str(self.gamma))
	# [init code]


	## Shows a visualization of the current state of the domain and that of learning. See code
	# \ref Domain_show "Here".
	# @param s
	# The state that the domain is in
	# @param a
	# The action being performed
	# @param representation
	# The representation to show

	# [show code]
    def show(self,s,a, representation):
        self.showDomain(s,a)
        self.showLearning(representation)
	# [show code]


    ## \b ABSTRACT \b METHOD: Shows a visualization of the current state of the domain. See code
	# \ref Domain_showDomain "Here".
	# @param s
	# The state that the domain is in
	# @param a
	# The action being performed

	# [showDomain code]
    def showDomain(self,s,a = 0):
        pass
	# [showDomain code]


    ## \b ABSTRACT \b METHOD: Shows a visualization of the current learning. This visualization is usually in the form
    # of a value gridded value function and policy. It is thus really only possible for 1 or 2-state domains. See code
	# \ref Domain_showLearning "Here".
	# @param representation
	# The representation to show

	# [showLearning code]
    def showLearning(self,representation):
        pass
	# [showLearning code]


    ## Returns the initial state of the %Domain
	# @return
	# A numpy array that defines the initial state of the %Domain. See code
	# \ref Domain_s0 "Here".

	# [s0 code]
    def s0(self):
        abstract
	# [s0 code]


    ## Returns all actions in the domain.
	# The default version returns all actions [0, 1, 2...].
    # You may want to change this method in your domain if all actions are not available at all times. See code
	# \ref Domain_possActions "Here".
	# @return
	# A numpy array that contains a list of every action in the domain.

	# [possActions code]
    def possibleActions(self,s):
        return arange(self.actions_num)
	# [possActions code]


    ## \b ABSTRACT \b METHOD: Performs an action while in a specific state and updates the domain accordingly.
	# This function should return a reward that the agent acheives for the action, the next state that the domain/agent should be in,
	# and a boolean determining whether a goal or fail state has been reached. See code
	# \ref Domain_step "Here".
	# @param s
	# The state in which the action is to be performed
	# @param a
	# The action to perform
    # @return [r,ns,t] => Reward (int), next state (state), isTerminal (bool)

	# [step code]
    def step(self,s,a):
        abstract
	# [step code]


	# \b ABSTRACT \b METHOD: Each row of output corresponds to a possible result from taking action a while in state s.
    # e.g. s,a -> r[i], ns[i], t[i] with probability p[i]. See code
	# \ref Domain_exStep "Here".
	# @param s
	# The given state
	# @param a
	# The given Action
    # @return p, r, ns, t. Probability of transition (float), Reward (int), next state (state), isTerminal (bool)

	# [exStep code]
    #def expectedStep(self,s,a):
    #			abstract
	# [exStep code]



    ## Determines whether the stats s is a terminal state.
	# The default definition does not terminate. Override this function to specify otherwise. See code
	# \ref Domain_isTerminal "Here".
	# @param s
	# The state to be examined
	# @return
	# True if the state is a terminal state, False otherwise.

	# [isTerminal code]
    def isTerminal(self,s):
        return False
	# [isTerminal code]


	## Run the environment by performing random actions for T steps. See code
	# \ref Domain_test "Here".
	# @param T
	# The desired number of steps

	# [test code]
    def test(self,T):
        terminal    = True
        steps       = 0
        while steps < T:
            if terminal:
                if steps != 0: self.showDomain(s,a)
                s = self.s0()
            elif steps % self.episodeCap == 0:
                s = self.s0()
            a = randSet(self.possibleActions(s))
            self.showDomain(s,a)
            r,s,terminal = self.step(s, a)
            steps += 1
	# [test code]


	## Prints the class data. See code
	# \ref Domain_test "Here".

	# [printAll code]
    def printAll(self):
        printClass(self)
	# [printAll code]


	## Offsets discrete dimensions by 0.5 so that binning works properly. See code
	# \ref Domain_extendDiscreteDimensions "Here".

	# [extendDiscreteDimensions code]
    def extendDiscreteDimensions(self):
        # Store the original limits for other types of calculations
        self.discrete_statespace_limits = self.statespace_limits
        self.statespace_limits = self.statespace_limits.astype('float')
        for d in arange(self.state_space_dims):
             if not d in self.continuous_dims:
                 self.statespace_limits[d,0] += -.5
                 self.statespace_limits[d,1] += +.5

	# [extendDiscreteDimensions code]


	## Sample a set number of next states and rewards from the domain. See code
	# \ref sampleStep "Here".
	# @param s
	# The given state
	# @param a
	# The given action
	# @param no_samples
	# The number of next states and rewards to be sampled.
	# @return
	# [S,A] => S is an array of next states, A is an array of rewards for those states

	# [sampleStep code]
    def sampleStep(self,s,a,no_samples):

        next_states = []
        rewards = []

        for i in arange(0,no_samples):

            r,ns,terminal = self.step(s, a)

            next_states.append(ns)
            rewards.append(r)

        return array(next_states),array(rewards)
	# [sampleStep code]


	## Returns a state sampled uniformely from the state space. See code
	# \ref Domain_s0uniform "Here".
	# @return
	# The state

	# [s0uniform code]
    def s0uniform(self):
        if className(self) == 'BlocksWorld':
            print "s0uniform is not supported by %s.\nFurther implementation is needed to filter impossible states." % className(self)
        if self.continuous_dims == []:
            s = empty(self.state_space_dims, dtype = integer)
        else:
            s = empty(self.state_space_dims)

        for d in arange(self.state_space_dims):
            a,b = self.statespace_limits[d]
            s[d] = random.rand()*(b-a)+a
            if not d in self.continuous_dims:
                s[d] = int(s[d])
        if len(s) == 1: s = s[0]
        return s
	# [s0uniform code]


	## Caps each element of the state space to lie within the allowed state limits.
	#This function is used for cases when state vector has elements outside of its limits. See code
	# \ref Domain_saturateState "Here".
	# @param s
	# A given state
	# @return
	# If s lies within statespace limits, return s unchanged; otherwise return the statespace_limit closest to s
	# e.g. discrete_statespace_limits = [0, 10] and s = [12], return [10].

	# [saturateState code]
    def saturateState(self,s):
        return bound_vec(s,self.discrete_statespace_limits)
	# [saturateState code]
