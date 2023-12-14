from env import ExpertOptionTradingEnv
from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam
from rl.agents import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory

# Check the environment
env = ExpertOptionTradingEnv()
# Get the environment's shape to set up the neural network
num_actions = env.action_space.n
obs_shape = env.observation_space.shape
print("Observation Shape:", obs_shape) 
# Define the neural network model
model = Sequential()
model.add(Flatten(input_shape=(1,) + obs_shape))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(num_actions))
model.add(Activation('linear'))

# Configure and compile the agent
memory = SequentialMemory(limit=50000, window_length=1)
policy = BoltzmannQPolicy()
dqn = DQNAgent(model=model, nb_actions=num_actions, memory=memory, nb_steps_warmup=10,
               target_model_update=1e-2, policy=policy)
dqn.compile(Adam(learning_rate=1e-3), metrics=['mae'])

dqn.fit(env, nb_steps=10000, visualize=False, verbose=2)

dqn.save_weights('dqn_expert_option_trader_weights.h5f', overwrite=True)
