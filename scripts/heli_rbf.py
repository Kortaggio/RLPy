#See http://acl.mit.edu/RLPy for documentation and future code updates

#Copyright (c) 2013, Alborz Geramifard, Robert H. Klein, and Jonathan P. How
#All rights reserved.

#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

#Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

#Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

#Neither the name of ACL nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#!/usr/bin/python
######################################################
# Developed by Alborz Geramiard Oct 25th 2012 at MIT #
######################################################


from Domains import HelicopterHover
from Agents import SARSA
from Representations import RBF
from Policies import eGreedy
from Tools import Logger

# Etc
#----------------------
PERFORMANCE_CHECKS  = 15
LEARNING_STEPS      = 5000 # Max number of learning steps
EXPERIMENT_NAMING   = ['domain','representation','max_steps','representation.batchThreshold']
PROJECT_PATH="Results/Temp"
jobID=-1
SHOW_ALL            = False
SHOW_PERFORMANCE    = True
PLOT_PERFORMANCE    = True
LOG_INTERVAL        = 1  # if make_exp_name = false then we assume the job is running on the cluster hence increase the intervals between logs to reduce output txt size
JOB_ID              = 1
PROJECT_PATH        = '.'
logger              = Logger()
MAX_ITERATIONS      = 10

#Agent ----------------------
alpha_decay_mode        = 'Boyan' # Boyan works better than dabney in some large domains such as pst. Decay rate parameter; See Agent.py initialization for more information
initial_alpha           = 1
boyan_N0                = 1000
LAMBDA                  = 0.5


domain          = HelicopterHover(logger=logger)
representation  = RBF(domain, logger, rbfs=200, id=JOB_ID)
policy          = eGreedy(representation, logger, epsilon=0.05)

agent           = SARSA(representation, policy, domain, logger, initial_alpha,
                        LAMBDA, alpha_decay_mode, boyan_N0)
#agent           = Q_LEARNING(representation,policy,domain,logger,initial_alpha,LAMBDA, alpha_decay_mode, boyan_N0)
#agent           = LSPI(representation,policy,domain,logger,LEARNING_STEPS, LEARNING_STEPS/PERFORMANCE_CHECKS, LSPI_iterations, epsilon = LSPI_WEIGHT_DIFF_TOL, return_best_policy = LSPI_return_best_policy,re_iterations = RE_LSPI_iterations, use_sparse = LSPI_use_sparse)
#agent           = LSPI_SARSA(representation,policy,domain,logger,LSPI_iterations,LSPI_windowSize,LSPI_WEIGHT_DIFF_TOL,RE_LSPI_iterations,initial_alpha,LAMBDA,alpha_decay_mode, boyan_N0)

if __name__ == '__main__':
    from Experiments import OnlineExperiment
    experiment = OnlineExperiment(agent, domain, logger,
                                  exp_naming=EXPERIMENT_NAMING,
                                  id=JOB_ID, max_steps=LEARNING_STEPS,
                                  show_all=SHOW_ALL,
                                  performanceChecks=PERFORMANCE_CHECKS,
                                  show_performance=SHOW_PERFORMANCE,
                                  log_interval=LOG_INTERVAL,
                                  project_path=PROJECT_PATH,
                                  plot_performance=PLOT_PERFORMANCE)

    experiment.run()
    experiment.save()
