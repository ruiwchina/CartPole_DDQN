import numpy as np
import random
from collections import deque
from keras.models import Sequential
from keras.layers import Dense, Conv2D, Dropout, Flatten
from keras.optimizers import Adam, Nadam, Adamax


class Agent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.98   # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.00  # exploration will not decay futher
        self.epsilon_decay = 0.000995
        self.learning_rate = 0.001
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.weight_backup = 'model_weights.h5'
        self.f = open('csvfile.csv', 'w')

    def _build_model(self):
        model = Sequential()
        model.add(Dense(20, input_dim=self.state_size, activation='relu'))
        model.add(Dense(20, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return model

    def save_model(self):
            self.model.save(self.weight_backup)

    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])

    def remember(self, state, action, reward, new_state, done):
        self.memory.append((state, action, reward, new_state, done))

    def memory_replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
        Sample = random.sample(self.memory, batch_size)
        for state, action, reward, new_state, done in Sample:
            target = reward
            if not done:
                future_action = self.model.predict(new_state)[0]
                future_q = self.target_model.predict(new_state)[0]
                target = reward + self.gamma * future_q[np.argmax(future_action)]
            target_f = self.model.predict(state)
            target_f[0][action] = target
            history = self.model.fit(state, target_f, epochs=1, verbose=0)
        self.f.write('{}, {}\n'.format(history.history['loss'][0], target_f[0][action])) #Give your csv text here.
        if self.epsilon > self.epsilon_min:
            self.epsilon -= self.epsilon_decay
