import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

# NEW MODULES
from collections import defaultdict
from operator import itemgetter

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        #=======================================================================
        # TODO: Initialize any additional variables here
        
        # Q value table
        self.Q = defaultdict(dict)
        
        # learning rate
        self.LR = 0.9
        
        # discount factor
        self.DF = 0.4
        
        # randomness introduced upon action selection
        # 1: totally randome; 0: no random selection
        self.randomness = 0.05
        
        #
        self.penalties = 0
        #=======================================================================
        
    def build_state_tuple(self, waypoint, inputs):
        return (waypoint, inputs['light'], inputs['oncoming'], inputs['left'])
        
    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.penalties = 0

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = self.build_state_tuple(self.next_waypoint, inputs)

        # After observing a new state, update the Q table
        if self.state != None and not(self.state in self.Q.keys()):
            for action in self.env.valid_actions:
                self.Q[self.state][action] = 1.
        
        # TODO: Select action according to your policy
        action = self.get_next_action()

        # Execute action and get reward
        reward = self.env.act(self, action)
        if (reward < 0):
            self.penalties += 1
            #print "{}, {}, {}".format(inputs, self.next_waypoint, action)

        # TODO: Learn policy based on state, action, reward
        self.update_Q(t, action, reward)
        
        #print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]
        
    # NEW FUNCTIONS
    #===========================================================================
    def get_optimal_action(self, state):
        
        actions = self.Q[state]
        #return max(actions, key=actions.get)
        optimal_actions = []
        maxQ = max(actions.values())
        
        # find all the actions that have the max Q value
        for key, value in actions.iteritems():
            if value == maxQ:
                optimal_actions.append(key)
        
        # if the optimal action is not unique, randomly choose one
        if len(optimal_actions) > 1:
            return random.choice(optimal_actions)
        else:
            return optimal_actions[0]
    
    
    def get_next_action(self):
        
        optimal_action = self.get_optimal_action(self.state)
        if random.random() < self.randomness:
            random_actions = [action for action in self.env.valid_actions if action != optimal_action]
            return random.choice(random_actions)
        else:
            return optimal_action
    
    
    def update_Q(self, t, action, reward):
        
        next_waypoint2 = self.planner.next_waypoint()
        next_inputs = self.env.sense(self)
        next_state = self.build_state_tuple(next_waypoint2, next_inputs)
        
        # check if the 'next_waypoint' for next_state is None
        if next_waypoint2 != None:
            if not(next_state in self.Q.keys()):
                for action in self.env.valid_actions:
                    self.Q[next_state][action] = 1.
            old = self.Q[self.state][action]
            next_optimal_action = self.get_optimal_action(next_state)
            next_Q = self.Q[next_state][next_optimal_action]
            self.Q[self.state][action] = (1. - self.LR) * old + self.LR * (reward + self.DF * next_Q)
        else:
            return
    #===========================================================================


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0., display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line
    
    # print the final Q table
    q = e.primary_agent.Q
    for i in q.keys():
        j = q[i].keys()
        print "({:7}, {:5}, {:7}, {:7}):{:7}:{: 0.2f},{:5}:{: 0.2f},{:4}:{: 0.2f},{:4}:{: 0.2f}".format(i[0], i[1], i[2], i[3], j[0], q[i][j[0]], j[1], q[i][j[1]], j[2], q[i][j[2]], j[3], q[i][j[3]])

if __name__ == '__main__':
    run()
