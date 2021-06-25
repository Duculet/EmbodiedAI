import sys
import time
import csv
import os

import matplotlib.pyplot as plt
import pygame

from typing import Union, Tuple

from experiments.aggregation.aggregation import Aggregations
from experiments.covid.population import Population
from experiments.flocking.flock import Flock
from experiments.covid.config import config


def _plot_covid(data, hospitalised=1, infected=1, num_agents=1) -> None:
    """
    Plot the data related to the covid experiment. The plot is based on the number of Susceptible,
    Infected and Recovered agents

    Args:
    ----
        data:

    """
    # output_name = "experiments/covid/plots/Covid-19-SIR%s.png" % time.strftime(
    #     "-%m.%d.%y-%H:%M", time.localtime()
    # )
    # output_name = "experiments/covid/plots/Covid-19-SIR-%s%s.png" % ("&".join(configuration), time.strftime(
    #     "-%m.%d.%y-%H:%M", time.localtime()))

    # max_frames = config["screen"]["frames"]
    # if len(data["S"]) != max_frames:
    #     for key in data.keys():
    #         data[key] = data[key][-max_frames:]
    #         print(len(data[key]))
    current_path = config["screen"]["current_path"]
    current_run = config["screen"]["current_run"]

    path = current_path + "plots/"
    if not os.path.exists(path):
        os.mkdir(path)

    output_name = current_path

    if current_run:
        output_name += "plots/%d.png" % current_run

    fig = plt.figure()
    plt.plot(data["S"], label="Susceptible", color=(1, 0.5, 0))  # Orange
    plt.plot([i + q for i, q in zip(data["I"], data["Q"])],
             label="Infected", color=(1, 0, 0))  # Red
    plt.plot(data["R"], label="Recovered", color=(0, 1, 0))  # Green
    plt.plot(data["Q"], label="Quarantined", color=(0, 0, 1))  # Blue
    plt.plot(data["D"], label="Dead", color=(1, 0, 1))  # Purple
    plt.plot(data["V"], label="Vaccinated", color=(0, 0, 0))  # Black
    plt.title("Covid-19 Simulation S-I-R")
    plt.xlabel("Time")
    plt.ylabel("Population")
    plt.legend()
    fig.savefig(output_name)

    infection_rate = round(infected / (num_agents - data["V"][-1]), 2) * 100
    hospitalization_rate = round(hospitalised / num_agents, 2) * 100
    death_rate = round(data["D"][-1] / num_agents, 2) * 100
    vaxxed_ratio = round(data["V"][-1] / num_agents, 2) * 100

    # open the file in the write mode
    with open(current_path + 'results.csv', 'a', encoding='utf-8', newline='') as f:
        # create the csv writer
        writer = csv.writer(f)
        # write a row to the csv file
        writer.writerow(["Infection rate:", infection_rate, "%"])
        writer.writerow(["Hospitalization rate:", hospitalization_rate, "%"])
        writer.writerow(["Death rate:", death_rate, "%"])
        writer.writerow(["Vaccinated ratio:", vaxxed_ratio, "%"])
        writer.writerow(["-", "Done", current_run])

    # print("-" * 50)
    # print("Results:")
    # print("Infection rate:", infection_rate)
    # print("Hospitalization rate:", hospitalization_rate)
    # print("Death rate:", death_rate)
    # print("Vaccinated ratio:", vaxxed_ratio)


def _plot_flock() -> None:
    """Plot the data related to the flocking experiment. TODO"""
    pass


def _plot_aggregation() -> None:
    """Plot the data related to the aggregation experiment. TODO"""
    pass


"""
General simulation pipeline, suitable for all experiments
"""


class Simulation:
    """
    This class represents the simulation of agents in a virtual space.
    """

    def __init__(
            self,
            num_agents: int,
            screen_size: Union[Tuple[int, int], int],
            swarm_type: str,
            iterations: int):
        """
        Args:
        ----
            num_agents (int):
            screen_size (Union[Tuple[int, int], int]):
            swarm_type (str):
            iterations (int):
        """
        # general settings
        self.screensize = screen_size
        self.screen = pygame.display.set_mode(screen_size)
        self.sim_background = pygame.Color("gray21")
        self.iter = iterations
        self.swarm_type = swarm_type

        self.FPS = config['screen']['fps']  # frames per second setting

        # swarm settings
        self.num_agents = num_agents
        if self.swarm_type == "flock":
            self.swarm = Flock(screen_size)

        elif self.swarm_type == "aggregation":
            self.swarm = Aggregations(screen_size)

        elif self.swarm_type == "covid":
            plot = {"S": [], "I": [], "R": [], "Q": [], "D": [], "V": []}
            self.swarm = Population(screen_size, plot)

        else:
            print("None of the possible swarms selected")
            sys.exit()

        # update
        self.to_update = pygame.sprite.Group()
        self.to_display = pygame.sprite.Group()
        self.running = True

    def plot_simulation(self) -> None:
        """Depending on the type of experiment, plots the final data accordingly"""
        if self.swarm_type == "covid":
            _plot_covid(self.swarm.points_to_plot,
                        self.swarm.hospitalised, self.swarm.infected, self.num_agents)

        elif self.swarm_type == "flock":
            _plot_flock()

        elif self.swarm_type == "aggregation":
            _plot_aggregation()

    def initialize(self) -> None:
        """Initialize the swarm, specifying the number of agents to be generated"""

        # initialize a swarm type specific environment
        self.swarm.initialize(self.num_agents)

    def simulate(self) -> None:
        """Here each frame is computed and displayed"""
        self.screen.fill(self.sim_background)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        self.swarm.update()
        self.swarm.display(self.screen)

        fpsClock = pygame.time.Clock()
        pygame.display.flip()
        fpsClock.tick(self.FPS)

    def run(self) -> None:
        """
        Main cycle where the initialization and the frame-by-frame computation is performed.
        The iteration con be infinite if the parameter iter was set to -1, or with a finite number of frames
        (according to iter)
        When the GUI is closed, the resulting data is plotted according to the type of the experiment.
        """
        # initialize the environment and agent/obstacle positions
        self.initialize()
        # the simulation loop, infinite until the user exists the simulation
        # finite time parameter or infinite

        if self.iter == float("inf"):

            while self.running:
                init = time.time()
                self.simulate()
                # print(time.time() - init)

            self.plot_simulation()
        else:
            start = time.time()
            for i in range(self.iter):
                self.simulate()
            end = time.time()
            self.plot_simulation()
            print("Time elapsed:", end - start)
            print("-" * 50)
