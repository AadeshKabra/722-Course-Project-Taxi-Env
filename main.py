################################################################################################
# import gymnasium as gym
# import numpy as np
# import random
#
#
# env = gym.make('Taxi-v3', render_mode="human")
#
# state = env.reset()
#
# state_size = env.observation_space
# action_size = env.action_space
# print(state_size, action_size)
#
#
# env.s = 328
#
# epochs = 0
# penalties, rewards = 0, 0
#
# frames = []
#
# done = False
#
# while not done:
#     action = env.action_space.sample()
#     print(env.step(action))
#     observation, reward, done, truncated, info = env.step(action)
#     #
#     if reward == -10:
#         penalties += 1
#
#
#     frames.append({'frame': env.render(), 'state': state, 'action': action, reward: reward})
#
#     epochs += 1
#     # break
#
# print(epochs)
# print(penalties)


################################################################################################


# num_steps = 100
# for i in range(num_steps):
#     action = env.action_space.sample()
#     reward = env.step(action)
#     print(action, reward)
#
#     env.render()
#
# env.close()


# observation, info = env.reset()
#
# print(observation)
# print(info)
#
# for _ in range(100):
#     action = env.action_space.sample()
#     observation, reward, terminated, truncated, info = env.step(action)
#
#     # print("Observation: ", observation, "Reward: ", reward, "Terminated: ", terminated, "Info: ", info)
#     if terminated or truncated:
#         break
#
#
# print(env.render())
#
# env.close()



import gymnasium as gym


env = gym.make('Taxi-v3', render_mode="human")

state = env.reset()
state_size = env.observation_space
action_size = env.action_space


