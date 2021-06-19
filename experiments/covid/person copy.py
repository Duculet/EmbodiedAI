import numpy as np
import pygame

from experiments.covid.config import config
from simulation.agent import Agent
from simulation.utils import *
import time


class Person(Agent):
    """ """

    def __init__(
            self, pos, v, population, index: int, image: str = None, color="orange"
    ) -> None:

        super(Person, self).__init__(
            pos,
            v,
            image,
            color,
            max_speed=config["agent"]["max_speed"],
            min_speed=config["agent"]["min_speed"],
            width=config["agent"]["width"],
            height=config["agent"]["height"],
            dT=config["agent"]["dt"],
            index=index
        )
        self.population = population
        self.type = "S"

        self.p_quarantine = config["person"]["p_quarantine"]
        self.p_dead = config["person"]["p_dead"]

        self.wears_mask = False
        # policy measures in effect
        # 'none, 'inside_only', or 'always'
        self.mask_worn = config["person"]["mask"]
        # number of time_steps (0 is no quarantine)
        self.quarantine = config["person"]["quarantine"]
        # recommended distance (0 is no distancing)
        self.social_distancing = config["person"]["social_distancing"]
        # (boolean, start_time, end_time)
        self.curfew = config["person"]["curfew"]
        self.corona_app = config["person"]["corona_app"]  # 'True' or 'False'
        if config["person"]["p_infected"] > np.random.random():
            # print("INFECTED")
            self.current_state = 'infected'
            self.type = 'I'
            self.color = "red"
            self.image.fill(self.color)
            self.infection_timer = 0
        else:
            self.current_state = 'susceptible'

        # determine p_mask
        if self.mask_worn == 'none':
            self.p_mask = config["person"]["p_mask_none"]
        elif self.mask_worn == 'inside_only':
            self.p_mask = config["person"]["p_mask_inside_only"]
        else:  # if 'always'
            self.p_mask = config["person"]["p_mask_always"]

        if not self.wears_mask:
            if self.p_mask > np.random.random():
                self.wears_mask = True
            else:
                self.wears_mask = False

        self.p_infected_inside = config["person"]["p_infected_inside"]
        self.p_infected_outside = config["person"]["p_infected_outside"]

        self.age = np.random.randint(1, 101)
        self.Q = False

        self.incubation_period = config["person"]["incubation_period"] + np.random.normal(
            0, config["person"]["incubation_var"])

    def update_actions(self) -> None:
        # self.population.datapoints.append(self.type)
        if self.type != "D":
            for obstacle in self.population.objects.obstacles:
                collide = pygame.sprite.collide_mask(self, obstacle)
                if bool(collide):
                    self.avoid_obstacle()

        self.current_state = self.state_update(self.current_state)

    def state_update(self, current_state):
        new_state = current_state

        if current_state == 'susceptible':
            new_state = self.infection(current_state)
        elif current_state == 'infected':
            new_state = self.recovery(current_state)

        return new_state

    def infection(self, current_state):
        new_state = current_state

        sites = []
        if self.type != "D":
            for obstacle in self.population.objects.sites:
                collide = pygame.sprite.collide_mask(self, obstacle)
                if bool(collide):
                    sites.append(True)

        desired_distance = max(
            0, (self.social_distancing + np.random.normal(0, config["person"]["distance_var"])))
        
        self.n_neighbours = len(
            self.population.find_neighbors(self, desired_distance))

        # # determine mobility
        # if self.curfew[0] == True:
        #     # check if curfew-time is in effect
        #     if self.curfew[1] < time_of_day < self.curfew[2]:
        #         self.v = np.array([0, 0])
        #     else:
        #         pass
        #         # actions that person takes if he/she is out and about

        #         # if person gets infected

        if any(sites):
            if not self.wears_mask and self.n_neighbours and self.p_infected_inside > np.random.random():
                self.type = 'I'
                self.image.fill('blue')
                new_state = 'infected'
        else:
            if not self.wears_mask and self.n_neighbours >= 5 and self.p_infected_outside > np.random.random():
                self.type = 'I'
                self.image.fill('blue')
                new_state = 'infected'

        self.infection_timer = 0

        return new_state

    def recovery(self, current_state):
        new_state = current_state
        self.infection_timer += 1

        # check if person is recovered
        if self.infection_timer > config["person"]["min_recovery_period"]:
            if config["person"]["p_recovery"] > np.random.random():
                new_state = 'recovered'
                if self.type == 'Q':
                    self.pos = np.array([500.0, 275.0])
                    self.v = self.set_velocity()
                self.type = 'R'
                self.image.fill('green')

            return new_state
        
        if self.incubation_period < self.infection_timer < config["person"]["min_recovery_period"]:
            self.image.fill('red')
            if self.infection_timer % 400 == 0 and self.p_dead * self.age > np.random.random():
                self.type = 'D'
                self.image.set_alpha(0)
                new_state = 'dead'
            elif self.infection_timer % 100 == 0:
                if self.type != "Q" and self.p_quarantine > np.random.random():
                    self.type = 'Q'
                    self.pos = np.array([500.0, 150.0])
                    self.v = self.set_velocity()
                    self.p_quarantine = 0
                self.p_quarantine += 0.05

        # if self.infection_timer > self.incubation_period:
            
        #     if self.p_dead * self.age > np.random.random():
        #         self.type = 'D'
        #         self.image.set_alpha(0)
        #         new_state = 'dead'
        #     elif self.p_quarantine > np.random.random():
        #         # Quarantine


        # # check whether person knows he/she is infected
        # else:
        #     # determine p_mask
        #     if self.mask == 'none':
        #         p_mask = config["person"]["p_mask_none"],
        #     elif self.mask == 'inside_only':
        #         p_mask = config["person"]["p_mask_inside_only"],
        #     else:  # if 'always'
        #         p_mask = config["person"]["p_mask_always"],

        #     if np.random.random() > p_mask:
        #         wears_mask = True
        #     else:
        #         wears_mask = False

        #     # determine desired distance to other persons
        #     desired_distance = min(0, (self.social_distancing + np.random.normal(0,
        #                                                                          config["person"]["distance_var"])))

        #     # determine mobility
        #     if self.curfew[0] == True:
        #         # check if curfew-time is in effect
        #         if time_of_day > self.lock_down[1] and time_of_day < self.lock_down[2]:
        #             v = 0
        #         else:
        #             pass
        #             # actions that person takes if he/she is out and about

        #             # else:  # if person knows he/she is infected
        #             #     # check if quarantine period is in effect
        #             #     if self.infection_timer < self.quarantine:
        #             #         v = 0
        #             #         # actions if in quarantine
        return new_state

    def immunity(self, current_state):
        pass
