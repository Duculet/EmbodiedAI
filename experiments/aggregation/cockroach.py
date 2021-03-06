import numpy as np
import pygame

from typing import Tuple

from simulation.agent import Agent
from simulation.utils import normalize, truncate
from simulation.utils import *
from experiments.aggregation.config import config

"""
Specific cockroach properties and helperfunctions
"""


class Cockroach(Agent):
    """
    Class that represents a cockroach. This class inherits the behavior
    from the base class Agent.
    Attributes:
    ----------
        state:
        pos:
        direction:
        speed:
    """

    def __init__(
            self, pos, v, aggregation, index: int, image: str = "experiments/aggregation/images/ant.png"
    ) -> None:
        """
        Args: needs to be uodated for cockroach
        ----
        state:
        pos:
        """

        super(Cockroach, self).__init__(
            pos,
            v,
            image,
            max_speed=config["agent"]["max_speed"],
            min_speed=config["agent"]["min_speed"],
            mass=config["agent"]["mass"],
            width=config["agent"]["width"],
            height=config["agent"]["height"],
            dT=config["agent"]["dt"],
            index=index
        )

        self.state = "wandering"
        self.environment = "outside"
        self.aggregation = aggregation
        self.current_t = 0
        self.t_leave = 0

    def update_actions(self) -> None:
        """
        Every change between frames happens here. This function is called by the method "update" in the class Swarm,
        for every agent/object. Here, it is checked if there is an obstacle in collision (in which case it avoids it by
        going to the opposite direction), align force, cohesion force and separate force between the agent and its neighbors
        is calculated, and the steering force and direction of the agent are updated
        """
        for obstacle in self.aggregation.objects.obstacles:
            collide = pygame.sprite.collide_mask(self, obstacle)
            if bool(collide):
                self.avoid_obstacle()

        left_site, right_site = self.aggregation.objects.sites

        left_collide, right_collide = pygame.sprite.collide_mask(
            self, left_site), pygame.sprite.collide_mask(self, right_site)

        if bool(left_collide) or bool(right_collide):
            self.environment = "site"
        else:
            self.environment = "outside"

        self.state = self.state_update(self.state)

    def state_update(self, current_state):
        """
        Function to decide state of the agent
        Args:
            current_state
        """
        self.n_neighbours = len(self.aggregation.find_neighbors(
            self, config["cockroach"]["radius_view"]))

        if current_state == 'wandering':
            new_state = self.join(current_state)
        elif current_state == 'joining':
            new_state = self.still(current_state)
        elif current_state == 'still':
            new_state = self.leave(current_state)
        else:  # if state is leaving
            new_state = self.wandering(current_state)

        return new_state

    def join(self, current_state):
        """
        Function to decide if agent joins an aggregation
        Args:
        ----
             current_state:
        """
        # determine p_join if entering a site
        if self.environment == 'site':

            p_join = (
                config["cockroach"]["p_join_base"]
                + self.n_neighbours * config["cockroach"]["join_weight"]
            )

            if self.n_neighbours >= config["cockroach"]["critical_mass"]:
                p_join = 1
            elif p_join > config["cockroach"]["p_join_max"]:
                p_join = config["cockroach"]["p_join_max"]

            # decide new state based on p_join
            if p_join > np.random.random():
                # reset timer
                self.current_t = 0
                # set stop time (after which cockroach switches to state 'still')
                self.t_stop = config["cockroach"]["t_stop"] \
                    + int(np.random.normal(0,
                          config["cockroach"]["t_stop_var"]))
                new_state = 'joining'

            # if cockroach decides not to join, it enters the 'leaving state'
            else:
                new_state = 'leaving'

            return new_state
        else:
            # Random direction change with a predefined probability
            p_change_direction = config["cockroach"]["p_change"]
            if p_change_direction > np.random.random():
                self.v = self.set_velocity()

            return current_state

    def still(self, current_state):
        """
        Function to decide if agent halts
        Args:
             current_state
        ----
        """
        self.current_t += 1

        # check stop timer and environment
        if self.current_t > self.t_stop and self.environment == 'site':
            new_state = 'still'
            self.v = np.array([0, 0])
        elif self.current_t > self.t_stop and self.environment != 'site':
            new_state = 'wandering'
        else:
            new_state = current_state

        return new_state

    def leave(self, current_state):
        """
        Function to decide if agent leaves an aggregation
        Args:
        ----
            current_state
        """

        # determine p_leave
        p_leave = (
            config["cockroach"]["p_leave_base"]
            - self.n_neighbours * config["cockroach"]["leave_weight"]
        )

        if self.n_neighbours >= config["cockroach"]["critical_mass"]:
            p_leave = 0
        elif p_leave < config["cockroach"]["p_leave_min"]:
            p_leave = config["cockroach"]["p_leave_min"]

        # decide new state based on p_leave
        if p_leave > np.random.random():
            # reset timer
            self.current_t = 0
            # set leave_time
            self.t_leave = config["cockroach"]["t_leave"] + \
                int(np.random.normal(0, config["cockroach"]["t_leave_var"]))
            new_state = 'leaving'
        else:
            new_state = current_state

        return new_state

    def wandering(self, current_state):
        """
        Function to decide if agent starts wandering
        Args:
        ----
        """

        check_still = self.v == np.asarray([0, 0])
        if check_still.all():
            self.v = self.set_velocity()

        self.current_t += 1

        if self.current_t < self.t_leave:
            new_state = 'wandering'
        else:
            new_state = current_state

        return new_state
