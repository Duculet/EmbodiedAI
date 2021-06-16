import numpy as np
from typing import Tuple
from experiments.aggregation.cockroach import Cockroach
from experiments.aggregation.config import config
from simulation.utils import *
from simulation.swarm import Swarm
from simulation.agent import Agent


class Aggregations(Swarm):  # also access methods from the super class Swarm
    """
    Specific aggregation properties, and aggregationing environment definition. This class inherits from the base class Swarm.
    It collects every element (agents, sites, and sites) of the simulation, and is in charge of commanding each
    agent to update its state, and display the new states frame by frame

    Attributes:
        object_loc

    """

    def __init__(self, screen_size) -> None:
        """
        This function is the initializer of the class aggregation.
        :param screen_size:
        """
        super(Aggregations, self).__init__(screen_size)
        self.object_loc = config["base"]["object_location"]

    def initialize(self, num_agents: int) -> None:
        """
        Initialize the whole swarm, creating and adding the obstacle objects, and the agent, placing them inside of the
        screen and avoiding the sites.
        :param num_agents: int:

        """

        # add obstacle/-s to the environment if present
        if config["aggregation"]["sites"]:
            object_loc = config["base"]["object_location"]
            left_object_loc = config["base"]["left"]
            right_object_loc = config["base"]["right"]

            scale = None

            if config["aggregation"]["one"]:
                scale = [100, 100]
            else:
                scale_l = config["base"]["left_size"]
                scale_r = config["base"]["right_size"]

            scale_large = [800, 800]

            filename = (
                "experiments/flocking/images/redd.png"
            )

            self.objects.add_object(
                file=filename, pos=object_loc, scale=scale_large, obj_type="obstacle"
            )

            if scale:
                filename = (
                    "experiments/aggregation/images/greyc1.png"
                )

                self.objects.add_object(
                    file=filename, pos=object_loc, scale=scale, obj_type="site"
                )
            else:
                if scale_l == scale_r:
                    filename = (
                        "experiments/aggregation/images/greyc1.png"
                    )
                    self.objects.add_object(
                        file=filename, pos=left_object_loc, scale=scale_l, obj_type="site"
                    )
                    self.objects.add_object(
                        file=filename, pos=right_object_loc, scale=scale_r, obj_type="site"
                    )
                else:

                    if scale_l < scale_r:
                        filename_left = (
                            "experiments/aggregation/images/greyc1.png"
                        )
                        filename_right = (
                            "experiments/aggregation/images/greyc2.png"
                        )
                    else:
                        filename_left = (
                            "experiments/aggregation/images/greyc2.png"
                        )
                        filename_right = (
                            "experiments/aggregation/images/greyc1.png"
                        )

                    self.objects.add_object(
                        file=filename_left, pos=left_object_loc, scale=scale_l, obj_type="site"
                    )

                    self.objects.add_object(
                        file=filename_right, pos=right_object_loc, scale=scale_r, obj_type="site"
                    )

            min_x, max_x = area(object_loc[0], scale_large[0])
            min_y, max_y = area(object_loc[1], scale_large[1])

        # add agents to the environment
        for index, agent in enumerate(range(num_agents)):
            coordinates = generate_coordinates(self.screen)

            # if sites present re-estimate the corrdinates
            if config["aggregation"]["sites"]:
                while (coordinates[0] >= max_x
                        or coordinates[0] <= min_x
                        or coordinates[1] >= max_y
                        or coordinates[1] <= min_y
                       ):
                    coordinates = generate_coordinates(self.screen)

            self.add_agent(Cockroach(pos=np.array(coordinates),
                           v=None, aggregation=self, index=index))

    def find_neighbor_velocity_center_separation(self, cockroach: Agent, neighbors: list) -> Tuple[float, float, float]:
        """
        Compute the total averaged sum of the neighbors' velocity, position and distance with regards to the considered
        agent
        :param cockroach: Agent
        :param neighbors: list

        """
        neighbor_sum_v, neighbor_sum_pos, separate = (
            np.zeros(2),
            np.zeros(2),
            np.zeros(2),
        )

        for neigh in neighbors:
            neighbor_sum_v += neigh.v
            neighbor_sum_pos += neigh.pos
            difference = (
                cockroach.pos - neigh.pos
            )  # compute the distance vector (v_x, v_y)
            difference /= norm(
                difference
            )  # normalize to unit vector with respect to its maginiture
            separate += difference  # add the influences of all neighbors up

        return neighbor_sum_v / len(neighbors), neighbor_sum_pos / len(neighbors), separate / len(neighbors)
