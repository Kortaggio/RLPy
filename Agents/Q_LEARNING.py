#See http://acl.mit.edu/RLPy for documentation and future code updates

#Copyright (c) 2013, Alborz Geramifard, Robert H. Klein, and Jonathan P. How
#All rights reserved.

#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

#Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

#Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

#Neither the name of ACL nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

######################################################
# Developed by Alborz Geramiard Oct 25th 2012 at MIT #
# Extended to Q-learning by Girish Chowdhary Nov 20th 2012 at MIT #
######################################################
from Agent import *
class Q_LEARNING(Agent):
    lambda_ = 0        #lambda Parameter in SARSA [Sutton Book 1998]
    eligibility_trace   = []
    eligibility_trace_s = [] # eligibility trace using state only (no copy-paste), necessary for dabney decay mode
    def __init__(self, representation, policy, domain,logger, initial_alpha =.1, lambda_ = 0, alpha_decay_mode = 'dabney', boyan_N0 = 1000):
        self.eligibility_trace  = zeros(representation.features_num*domain.actions_num)
        self.eligibility_trace_s= zeros(representation.features_num) # use a state-only version of eligibility trace for dabney decay mode
        self.lambda_            = lambda_
        super(Q_LEARNING,self).__init__(representation,policy,domain,logger,initial_alpha,alpha_decay_mode, boyan_N0)
        self.logger.log("Alpha_0:\t\t%0.2f" % initial_alpha)
        self.logger.log("Decay mode:\t\t"+str(alpha_decay_mode))
        
        if lambda_: self.logger.log("lambda:\t%0.2f" % lambda_)
    def learn(self,s,a,r,ns,na,terminal):
        gamma               = self.representation.domain.gamma
        theta               = self.representation.theta
        phi_s               = self.representation.phi(s)
        phi                 = self.representation.phi_sa(s,a,phi_s)
        phi_prime_s         = self.representation.phi(ns)
        na                  = self.representation.bestAction(ns,phi_prime_s) #Switch na to the best possible action
        phi_prime           = self.representation.phi_sa(ns,na,phi_prime_s)
        
        nnz                 = count_nonzero(phi_s)    #Number of non-zero elements
        if nnz == 0: # Phi has some nonzero elements, proceed with update
            return
        
        #Set eligibility traces:
        if self.lambda_:
            self.eligibility_trace   *= gamma*self.lambda_
            self.eligibility_trace   += phi
            
            self.eligibility_trace_s  *= gamma*self.lambda_
            self.eligibility_trace_s += phi_s
            
            #Set max to 1
            self.eligibility_trace[self.eligibility_trace>1] = 1
            self.eligibility_trace_s[self.eligibility_trace_s>1] = 1
        else:
            self.eligibility_trace    = phi
            self.eligibility_trace_s  = phi_s
        
        td_error            = r + dot(gamma*phi_prime - phi, theta)
        
        self.updateAlpha(phi_s,phi_prime_s,self.eligibility_trace_s, gamma, nnz, terminal)
        #
        theta               += self.alpha * td_error * self.eligibility_trace
        #print max(theta)
        #Discover features if the representation has the discover method
        discover_func = getattr(self.representation,'discover',None) # None is the default value if the discover is not an attribute
        if discover_func and callable(discover_func):
            expanded = self.representation.discover(phi_s,td_error)
        
            #Assuming one expansion for one interaction.
            if expanded and self.lambda_:
                    # Correct the size of eligibility traces (pad with zeros for new features)
                    self.eligibility_trace  = addNewElementForAllActions(self.eligibility_trace,self.domain.actions_num)
                    self.eligibility_trace_s = addNewElementForAllActions(self.eligibility_trace_s,1)

        if terminal: 
            self.episodeTerminated() 









