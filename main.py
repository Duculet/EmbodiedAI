import pygame
import time
import os
import csv

from experiments.covid.config import config
from simulation.simulation import Simulation
from itertools import product


"""
Code for multi-agent simulation in PyGame with/without physical objects in the environment
"""

parameters = list(product(config["environment"]["masks"],
                          config["environment"]["lockdowns"],
                          config["environment"]["p_vaccinations"]))

base_path = ""

if __name__ == "__main__":
    start = time.time()

    if config["screen"]["testing"]:
        for mask, lockdown, p_vax in parameters:
            path = f'experiments/covid/tests/{mask}-{lockdown}-{p_vax}/'
            config["screen"]["current_path"] = path
            if not os.path.exists(path):
                os.mkdir(path)
            with open(path + "results.csv", 'w', encoding="utf-8", newline='') as f:
                # create the csv writer
                writer = csv.writer(f)
                # write a row to the csv file
                writer.writerow(["Mask", "Lockdown", "P_Vax"])
                writer.writerow([mask, lockdown, p_vax])

            config["environment"]["mask"] = mask
            config["environment"]["lockdown"] = lockdown
            config["environment"]["p_vaccination"] = p_vax
            for i in range(1, config["screen"]["runs"] + 1):
                config["screen"]["current_run"] = i
                pygame.init()
                sim = Simulation(
                    num_agents=config["base"]["n_agents"],
                    screen_size=(config["screen"]["width"],
                                 config["screen"]["height"]),
                    swarm_type=config["base"]["swarm_type"],
                    iterations=config["screen"]["frames"])
                sim.run()
    else:
        path = "experiments/covid/tests/others/"
        config["screen"]["current_path"] = path
        if not os.path.exists(path):
            os.mkdir(path)
        with open(path + "results.csv", 'w', encoding="utf-8", newline='') as f:
            # create the csv writer
            writer = csv.writer(f)
            # write a row to the csv file
            writer.writerow(["Mask", "Lockdown", "P_Vax"])
            mask, lockdown, p_vax = config["environment"]["mask"], \
                config["environment"]["lockdown"], \
                config["environment"]["p_vaccination"]
            writer.writerow([mask, lockdown, p_vax])
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
