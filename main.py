import pygame
import time
import os

from experiments.covid.config import config
from simulation.simulation import Simulation
from itertools import product


"""
Code for multi-agent simulation in PyGame with/without physical objects in the environment
"""

parameters = list(product(config["environment"]["masks"],
                          config["environment"]["lockdowns"],
                          config["environment"]["p_vaccinations"]))

if __name__ == "__main__":
    start = time.time()
    # os.mkdir('experiments/covid/data/')
    file = open('experiments/covid/data/results.csv',
                'w', encoding='utf-8')
    file.close()
    for mask, lockdown, p_vax in parameters:
        config["environment"]["mask"] = mask
        config["environment"]["lockdown"] = lockdown
        config["environment"]["p_vaccination"] = p_vax
        pygame.init()
        sim = Simulation(
            num_agents=config["base"]["n_agents"],
            screen_size=(config["screen"]["width"],
                         config["screen"]["height"]),
            swarm_type=config["base"]["swarm_type"],
            iterations=config["screen"]["frames"])
        sim.run()
    end = time.time()
    print("Total runtime:", end - start)
