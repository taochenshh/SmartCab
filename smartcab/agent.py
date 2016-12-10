import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import numpy as np
from collections import namedtuple


input_keys = Environment.valid_inputs.keys()
input_keys.append('next_waypoint')
states = namedtuple('states',input_keys)
class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here

        # How likely we are gone explore new paths?
        self.epsilon = 0.05

        # Q learning update formula:
        # https://en.wikipedia.org/wiki/Q-learning
        # Good tutorial to start:
        # http://mnemstudio.org/path-finding-q-learning-tutorial.htm
        self.learning_rate = 0.90

        #the initial value of Q value
        self.default_q = 0

        # discount factor
        self.gamma = 0.10

        self.Q_values = {}
        
        self.prev_state = None
        self.prev_action = None
        self.prev_reward = None

        self.penalty_num = 0
        self.move_num = 0
 

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.state = None
        self.action = None
        self.reward = None


    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        
        # Update state
        self.state = states(light = inputs['light'], oncoming = inputs['oncoming'], left = inputs['left'], right = inputs['right'], next_waypoint = self.next_waypoint)

        # Select action according to your policy
        action, max_q_value = self.get_action(self.state)

        

        # Execute action and get reward
        reward = self.env.act(self, action)


        # update penalty_num and move_num
        self.move_num += 1
        if reward < 0:
        	self.penalty_num += 1

        

        self.save_state(self.state, action, reward)

        # Learn policy based on state, action, reward
        if self.prev_action != None:
            self.update_q_values(self.prev_state, self.prev_action, self.prev_reward, max_q_value)


        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


    def save_state(self, state, action, reward):
    	self.prev_state = self.state
        self.prev_action = action
        self.prev_reward = reward


    def update_q_values(self, prev_state, prev_action, prev_reward, max_q_value):
    	old_q_value = self.Q_values.get((prev_state,prev_action), self.default_q)
    	new_q_value = old_q_value + self.learning_rate * (prev_reward + self.gamma * max_q_value - old_q_value)
    	self.Q_values[(prev_state,prev_action)] = new_q_value


    def get_action(self, state):

        if random.random() < self.epsilon:
            action_selected = random.choice(self.env.valid_actions)
            q_value_selected = self.get_q_value(state, action_selected)
        else:
            # find the maximum Q-value
            q_value_selected = max([self.get_q_value(state, action_selected) for action_selected in self.env.valid_actions])
            # find action or actions associated with q_value_selected
            best_actions = [action for action in self.env.valid_actions if self.get_q_value(state, action) == q_value_selected]
            # randomly pick one action among the best:
            action_selected = random.choice(best_actions)
        return action_selected, q_value_selected

    def get_q_value(self, state, action):
    	return self.Q_values.get((state,action), self.default_q)


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.005, display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()

