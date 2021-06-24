from experiments.covid.config import config
from experiments.covid.person import Person
from simulation.swarm import Swarm
from simulation.utils import *


class Population(Swarm):
    """Class that represents the Population for the Covid experiment. TODO"""

    def __init__(self, screen_size, plot={"S": [], "I": [], "R": [], "Q": [], "D": [], "V": []}) -> None:
        super(Population, self).__init__(
            screen_size, plot)
        self.object_loc = config["base"]["object_location"]
        self.scale = [250, 250]
        self.quarantine_loc = [75, 75]
        self.quarantine_scale = [125, 125]

        self.split = config["environment"]["split"][0][0]
        self.split_scale = config["environment"]["split"][1]
        self.split_loc = config["environment"]["split"][2]
        self.split_loc_2 = [self.split_loc[0], self.split_loc[1] + 520]

        self.campus = config["environment"]["campus"][0][0]
        self.campus_scale = config["environment"]["campus"][1]
        self.campus_loc = config["environment"]["campus"][2]

        self.lockdown = config["environment"]["lockdown"]

        self.hospitalised = 0
        self.infected = 0

    def initialize(self, num_agents: int) -> None:
        """
        Args:
            num_agents (int):

        """
        if self.split:
            filename = (
                "experiments/covid/images/Sep.png"
            )
            self.objects.add_object(
                file=filename, pos=self.split_loc, scale=self.split_scale, obj_type="obstacle"
            )
            self.objects.add_object(
                file=filename, pos=self.split_loc_2, scale=self.split_scale, obj_type="obstacle"
            )
            # Left border
            self.objects.add_object(
                file=filename, pos=[0, 500], scale=[5, 1000], obj_type="obstacle"
            )
            # Right border
            self.objects.add_object(
                file=filename, pos=[1000, 500], scale=[5, 1000], obj_type="obstacle"
            )
            # Top border
            self.objects.add_object(
                file=filename, pos=[500, 0], scale=[1000, 5], obj_type="obstacle"
            )
            # Bottom border
            self.objects.add_object(
                file=filename, pos=[500, 1000], scale=[1000, 5], obj_type="obstacle"
            )
        elif self.campus:
            if self.lockdown:
                building_obstacle = (
                    "experiments/covid/images/Building_lock.png"
                )
                building_site = (
                    "experiments/covid/images/Building_site_lock.png"
                )
            else:
                building_obstacle = (
                    "experiments/covid/images/Building_spot.png"
                )
                building_site = (
                    "experiments/covid/images/Building_site.png"
                )
            for location in self.campus_loc:
                self.objects.add_object(
                    file=building_site, pos=location, scale=self.campus_scale, obj_type="site"
                )
                self.objects.add_object(
                    file=building_obstacle, pos=location, scale=self.campus_scale, obj_type="obstacle"
                )

            filename = (
                "experiments/covid/images/Hub.png"
            )
            self.objects.add_object(
                file=filename, pos=[500, 500], scale=self.campus_scale, obj_type="hub"
            )

            filename = (
                "experiments/covid/images/Quarantine_spot.png"
            )
            self.objects.add_object(
                file=filename, pos=[500, 150], scale=self.campus_scale, obj_type="obstacle"
            )

            min_x, max_x = area(
                500, self.campus_scale[0])
            min_y, max_y = area(
                150, self.campus_scale[1])

            separator = (
                "experiments/covid/images/Sep.png"
            )

            # Left border
            self.objects.add_object(
                file=separator, pos=[0, 500], scale=[5, 1000], obj_type="wall"
            )
            # Right border
            self.objects.add_object(
                file=separator, pos=[1000, 500], scale=[5, 1000], obj_type="wall"
            )
            # Top border
            self.objects.add_object(
                file=separator, pos=[500, 0], scale=[1000, 5], obj_type="wall"
            )
            # Bottom border
            self.objects.add_object(
                file=separator, pos=[500, 1000], scale=[1000, 5], obj_type="wall"
            )

        else:
            filename = (
                "experiments/covid/images/greyc1.png"
            )
            self.objects.add_object(
                file=filename, pos=self.object_loc, scale=self.scale, obj_type="site"
            )
            self.objects.add_object(
                file=filename, pos=[250, 250], scale=self.scale, obj_type="site"
            )
            self.objects.add_object(
                file=filename, pos=[750, 750], scale=self.scale, obj_type="site"
            )

            filename = (
                "experiments/covid/images/convex.png"
            )
            self.objects.add_object(
                file=filename, pos=self.quarantine_loc, scale=self.quarantine_scale, obj_type="obstacle"
            )

            min_x, max_x = area(
                self.quarantine_loc[0], self.quarantine_scale[0])
            min_y, max_y = area(
                self.quarantine_loc[1], self.quarantine_scale[1])

        # To Do
        # code snipet (not complete) to avoid initializing agents on obstacles
        # given some coordinates and obstacles in the environment, this repositions the agent

        to_avoid = [[50, 250], [400, 600], [750, 950]]

        if self.campus:
            if self.lockdown:
                for index, agent in enumerate(range(num_agents)):
                    coordinates = generate_coordinates(self.screen)
                    while(
                            to_avoid[0][0] <= coordinates[0] <= to_avoid[0][1] or
                            to_avoid[1][0] <= coordinates[0] <= to_avoid[1][1] or
                            to_avoid[2][0] <= coordinates[0] <= to_avoid[2][1]):
                        coordinates = generate_coordinates(
                            self.screen)

                    self.add_agent(Person(pos=np.array(coordinates),
                                          v=None, population=self, index=index))
            else:
                for index, agent in enumerate(range(num_agents)):
                    coordinates = generate_coordinates(self.screen)
                    while (min_x < coordinates[0] < max_x
                            or min_y < coordinates[1] < max_y
                           ):
                        coordinates = generate_coordinates(self.screen)

                    self.add_agent(Person(pos=np.array(coordinates),
                                          v=None, population=self, index=index))

        # if self.campus:
        #     # add agents to the environment
        #     if self.lockdown:
        #         for index, agent in enumerate(range(num_agents)):
        #             coordinates = generate_coordinates(self.screen)

        #             for id_obs, obstacle in enumerate(self.objects.obstacles):
        #                 if id_obs + 1 != len(self.objects.obstacles):
        #                     if index % len(self.objects.obstacles) == id_obs % len(self.objects.obstacles):
        #                         min_x, max_x = area(
        #                             obstacle.pos[0], obstacle.scale[0])
        #                         min_y, max_y = area(
        #                             obstacle.pos[1], obstacle.scale[1])
        #                         while (coordinates[0] >= max_x - 10
        #                                or coordinates[0] <= min_x + 10
        #                                or coordinates[1] >= max_y - 10
        #                                or coordinates[1] <= min_y + 10):
        #                             coordinates = generate_coordinates(
        #                                 self.screen)

        #                         self.add_agent(Person(pos=np.array(coordinates),
        #                                               v=None, population=self, index=index))
        #                         break
        #                 else:
        #                     while (min_x < coordinates[0] < max_x
        #                            or min_y < coordinates[1] < max_y
        #                            ):
        #                         coordinates = generate_coordinates(self.screen)
        #             # else:
        #             #     self.add_agent(Person(pos=np.array(coordinates),
        #             #                           v=None, population=self, index=index))

        #     else:
        #         for index, agent in enumerate(range(num_agents)):
        #             coordinates = generate_coordinates(self.screen)

        #             # if sites present re-estimate the corrdinates
        #             if config["population"]["obstacles"]:
        #                 while (min_x < coordinates[0] < max_x
        #                         or min_y < coordinates[1] < max_y
        #                        ):
        #                     coordinates = generate_coordinates(self.screen)

        #             self.add_agent(Person(pos=np.array(coordinates),
        #                                   v=None, population=self, index=index))

        else:
            for index, agent in enumerate(range(num_agents)):
                coordinates = generate_coordinates(self.screen)
                for obj in self.objects.obstacles:
                    rel_coordinate = relative(
                        coordinates, (obj.rect[0], obj.rect[1])
                    )
                    try:
                        while obj.mask.get_at(rel_coordinate):
                            coordinates = generate_coordinates(self.screen)
                            rel_coordinate = relative(
                                coordinates, (obj.rect[0], obj.rect[1])
                            )
                    except IndexError:
                        pass
                self.add_agent(Person(pos=np.array(coordinates),
                                      v=None, population=self, index=index))
