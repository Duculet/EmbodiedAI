import numpy as np
import pygame

from experiments.covid.config import config
from simulation.agent import Agent
from simulation.utils import *


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
            max_speed=config["agent"]["max_speed"] //
            2 if config["environment"]["lockdown"] else config["agent"]["max_speed"],
            min_speed=config["agent"]["min_speed"] //
            2 if config["environment"]["lockdown"] else config["agent"]["min_speed"],
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
        if 0.05 > np.random.random():
            # print("INFECTED")
            self.current_state = 'infected'
            self.type = 'I'
            self.color = "red"
            self.image.fill(self.color)
            self.infection_timer = 0
        else:
            self.current_state = 'susceptible'
        self.mobility_state = 'wandering'
        self.environment = "outside"
        self.current_t = 0
        self.t_leave = 0
        self.n_neighbours = 0
        self.pause = False

        # determine p_mask
        if self.mask_worn == 'none':
            self.p_mask = config["person"]["p_mask_none"]
        elif self.mask_worn == 'inside_only':
            self.p_mask = config["person"]["p_mask_inside_only"]
            # for obstacle in self.population.objects.sites:
            #     collide = pygame.sprite.collide_mask(self, obstacle)
            #     if bool(collide):
            #         self.p_mask = 0.95
        else:  # if 'always'
            self.p_mask = config["person"]["p_mask_always"]

        if not self.wears_mask:
            if self.p_mask > np.random.random():
                self.wears_mask = True
            else:
                self.wears_mask = False

    def update_actions(self) -> None:
        # self.population.datapoints.append(self.type)
        # check if agent is dead
        if self.type != "D":
            for obstacle in self.population.objects.obstacles:
                collide = pygame.sprite.collide_mask(self, obstacle)
                if bool(collide):
                    self.avoid_obstacle()

            for obstacle in self.population.objects.walls:
                collide = pygame.sprite.collide_mask(self, obstacle)
                if bool(collide):
                    self.avoid_obstacle()

            # determine desired distance to other persons
            self.desired_distance = max(
                0, (self.social_distancing + np.random.normal(0, config["person"]["distance_var"])))

            self.n_neighbours_out = len([neighbor for neighbor in self.population.find_neighbors(
                self, self.desired_distance // 4) if neighbor.environment == "outside"])
            self.n_neighbours_in = len([neighbor for neighbor in self.population.find_neighbors(
                self, self.desired_distance) if neighbor.environment == "site" or neighbor.environment == "hub"])

            for obstacle in self.population.objects.hubs:
                collide = pygame.sprite.collide_mask(self, obstacle)
                if bool(collide):
                    self.environment = "hub"
                else:
                    self.environment = "outside"

            for obstacle in self.population.objects.sites:
                collide = pygame.sprite.collide_mask(self, obstacle)
                if bool(collide):
                    self.environment = "site"
                    break

            if self.environment == 'hub':
                if self.dT == config["agent"]["dt"] and not self.pause:
                    self.dT /= 4
                    # print('-' * 50)
                    # print("OLD:", self.dT)
                    # print("NEW", self.dT)
            elif self.environment == 'site':
                if self.dT == config["agent"]["dt"] and not self.pause:
                    self.dT /= 2
                    # print('-' * 50)
                    # print("OLD:", self.dT)
                    # print("NEW", self.dT)
            else:
                if not(self.dT == config["agent"]["dt"]) and not self.pause:
                    self.dT = config["agent"]["dt"]
                    # print('-' * 50)
                    # print("OLD:", self.dT)
                    # print("NEW", self.dT)

        self.state_update()

    def state_update(self):

        if self.current_state == 'susceptible':
            self.infection()
        elif self.current_state == 'infected':
            self.recovery()

        if self.mobility_state == 'wandering':
            self.join()
        elif self.mobility_state == 'joining':
            self.still()
        elif self.mobility_state == 'still':
            self.leave()
        else:  # if state is leaving
            self.wandering()

    def join(self):
        """
        Function to decide if agent joins an aggregation
        """

        # for obstacle in self.population.objects.hubs:
        #     collide = pygame.sprite.collide_mask(self, obstacle)
        #     if bool(collide):
        #         self.environment = "hub"
        #     else:
        #         self.environment = "outside"

        # determine p_join if entering a site
        if self.environment == 'hub':

            p_join = (
                config["person"]["p_join_base"]
                + self.n_neighbours * config["person"]["join_weight"]
            )

            if self.n_neighbours >= config["person"]["critical_mass"]:
                p_join = 1
            elif p_join > config["person"]["p_join_max"]:
                p_join = config["person"]["p_join_max"]

            # decide new state based on p_join
            if p_join > np.random.random():
                # reset timer
                self.current_t = 0
                # set stop time (after which person switches to state 'still')
                self.t_stop = config["person"]["t_stop"] \
                    + int(np.random.normal(0,
                          config["person"]["t_stop_var"]))
                self.mobility_state = 'joining'
            # if person decides not to join, it enters the 'leaving state'
            else:
                self.mobility_state = 'leaving'
        else:
            # Random direction change with a predefined probability
            p_change_direction = config["person"]["p_change"]
            if p_change_direction > np.random.random():
                self.v = self.set_velocity()

    def still(self):
        """
        Function to decide if agent halts
        """
        self.current_t += 1

        # check stop timer and environment
        if self.current_t > self.t_stop and self.environment == 'hub':
            self.mobility_state = 'still'
            self.v = np.array([0, 0])
        elif self.current_t > self.t_stop and self.environment != 'hub':
            self.mobility_state = 'wandering'

    def leave(self):
        """
        Function to decide if agent leaves an aggregation
        """

        # determine p_leave
        p_leave = (
            config["person"]["p_leave_base"]
            - self.n_neighbours * config["person"]["leave_weight"]
        )

        if self.n_neighbours >= config["person"]["critical_mass"]:
            p_leave = 0
        elif p_leave < config["person"]["p_leave_min"]:
            p_leave = config["person"]["p_leave_min"]

        # decide new state based on p_leave
        if p_leave > np.random.random():
            # reset timer
            self.current_t = 0
            # set leave_time
            self.t_leave = config["person"]["t_leave"] + \
                int(np.random.normal(0, config["person"]["t_leave_var"]))
            self.mobility_state = 'leaving'

    def wandering(self):
        """
        Function to decide if agent starts wandering
        """

        check_still = self.v == np.asarray([0, 0])
        if check_still.all():
            self.v = self.set_velocity()

        self.current_t += 1

        if self.current_t < self.t_leave:
            self.mobility_state = 'wandering'

    def infection(self):

        # sites = []
        # if self.type != "D":
        #     for obstacle in self.population.objects.sites:
        #         collide = pygame.sprite.collide_mask(self, obstacle)
        #         if bool(collide):
        #             sites.append(True)

        # # determine mobility
        # if self.curfew[0] == True:
        #     # check if curfew-time is in effect
        #     if self.curfew[1] < time_of_day < self.curfew[2]:
        #         self.v = np.array([0, 0])
        #     else:
        #         pass
        #         # actions that person takes if he/she is out and about

        #         # if person gets infected

        if self.environment == "site":
            if not self.wears_mask and self.n_neighbours_in and 0.2 > np.random.random():
                self.type = 'I'
                self.image.fill('blue')
                self.current_state = 'infected'
        elif self.environment == "hub":
            if not self.wears_mask and self.n_neighbours_in and 0.2 > np.random.random():
                self.type = 'I'
                self.image.fill('blue')
                self.current_state = 'infected'
        else:
            if not self.wears_mask and self.n_neighbours_out and 0.4 > np.random.random():
                self.type = 'I'
                self.image.fill('blue')
                self.current_state = 'infected'

        self.infection_timer = 0

    def recovery(self):
        self.infection_timer += 1

        # check if person is recovered
        if self.infection_timer > config["person"]["min_recovery_period"]:
            if config["person"]["p_recovery"] > np.random.random():
                self.current_state = 'recovered'
                if self.type == 'Q':
                    self.pos = np.array([500.0, 275.0])
                    self.v = self.set_velocity()
                self.type = 'R'
                self.image.fill('green')

        elif self.infection_timer > config["person"]["incubation_period"]:
            self.image.fill('red')
            quarantine_period = config["person"]["incubation_period"] + abs(
                int(np.random.normal(0, config["person"]["incubation_var"])))
            if self.infection_timer < quarantine_period:
                if self.dT != 0:
                    self.dT = 0
                    self.pause = True
            else:
                if self.dT == 0:
                    self.dT = config["agent"]["dt"]
                    self.pause = False

                if config["person"]["p_onset"] > np.random.random():
                    if self.p_dead > np.random.random():
                        self.type = 'D'
                        self.image.fill('pink')
                        self.image.set_alpha(0)
                        self.current_state = 'dead'
                    elif self.p_quarantine > np.random.random():
                        # Quarantine
                        min_x, max_x = area(
                            500, self.population.campus_scale[0])
                        min_y, max_y = area(
                            150, self.population.campus_scale[1])
                        self.pos = np.array(
                            [randrange(min_x, max_x), randrange(min_y, max_y)])
                        self.v = self.set_velocity()
                        self.type = 'Q'
                    self.p_dead = 0
                    self.p_quarantine = 0

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
