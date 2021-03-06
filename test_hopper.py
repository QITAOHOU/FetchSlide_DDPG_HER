import torch
import os
import gym
import numpy as np

from networks.actor_critic import *

# process the inputs
def process_inputs(o, g, o_mean, o_std, g_mean, g_std, args):
    o_clip = np.clip(o, -args.clip_obs, args.clip_obs)
    g_clip = np.clip(g, -args.clip_obs, args.clip_obs)
    o_norm = np.clip((o_clip - o_mean) / (o_std), -args.clip_range, args.clip_range)
    g_norm = np.clip((g_clip - g_mean) / (g_std), -args.clip_range, args.clip_range)
    inputs = np.concatenate([o_norm, g_norm])
    inputs = torch.tensor(inputs, dtype=torch.float32)
    return inputs

def test_agent(args):
    path = os.path.join(args.model_dir, os.path.join(args.env_name,"actor.pth"))
    print(path)
    #o_mean, o_std, g_mean, g_std, model = torch.load(model, map_location=lambda storage, loc: storage)

    env = gym.make(args.env_name)
    observation = env.reset()
    print("Initial observation: ", observation)

    env_params = {
        'obs_dim' : observation.shape[0], #(25,)
        #'goal_dim': observation['desired_goal'].shape[0],  #(3,)
        'action_dim': env.action_space.shape[0], #(4,)
        'max_action' : env.action_space.high[0], # high : [1,1,1,1] low: [-1,-1,-1,-1]
    }

    # create instance of actor for testing model
    actor = Actor(env_params, False)
    actor.load_state_dict(torch.load(path))
    actor.eval()

    for episode in range(args.test_episodes):
        obs = env.reset()
        #obs = observation['observation']
        obs = torch.tensor(obs, dtype=torch.float32)
        #goal    = observation['desired_goal']
        for step in range(200):
            env.render()
            reward = 0
            #state = process_inputs(obs, goal, o_mean, o_std, g_mean, g_std, args)
            # get actions for current state
            with torch.no_grad():
                actions = actor(obs).cpu().numpy().squeeze()
            # carry out action
            if ("Pendulum" in args.env_name):
                obs_new, reward, _, info = env.step([actions])
            else:
                obs_new, reward, _, info = env.step(actions)
            # get next state
            obs = obs_new
            obs = torch.tensor(obs, dtype=torch.float32)
        print("Episode number : {} Reward : {}".format(episode, reward))
