from experiments.covid.config import config
from experiments.covid.person import Person
from simulation.swarm import Swarm
from simulation.utils import *


class Population(Swarm):
    """Class that represents the Population for the Covid experiment. TODO"""

    def __init__(self, screen_size, plot={"S": [], "I": [], "R": [], "Q": [], "D": []}) -> None:
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
                file=filename, pos=[500, 500], scale=self.campus_scale, obj_type="site"
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
                file=separator, pos=[0, 500], scale=[5, 1000], obj_type="obstacle"
            )
            # Right border
            self.objects.add_object(
                file=separator, pos=[1000, 500], scale=[5, 1000], obj_type="obstacle"
            )
            # Top border
            self.objects.add_object(
                file=separator, pos=[500, 0], scale=[1000, 5], obj_type="obstacle"
            )
            # Bottom border
            self.objects.add_object(
                file=separator, pos=[500, 1000], scale=[1000, 5], obj_type="obstacle"
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

        if self.campus:
            # add agents to the environment
            for index, agent in enumerate(range(num_agents)):
                coordinates = generate_coordinates(self.screen)

                # if sites present re-estimate the corrdinates
                if config["population"]["obstacles"]:
                    while (min_x < coordinates[0] < max_x
                            or min_y < coordinates[1] < max_y
                           ):
                        coordinates = generate_coordinates(self.screen)

                self.add_agent(Person(pos=np.array(coordinates),
                                      v=None, population=self, index=index))

        else:
            if config["population"]["obstacles"]:  # you need to define this variable
                for index, agent in enumerate(range(num_agents)):
                    coordinates = generate_coordinates(self.screen)
                    for obj in self.objects.obstacles:
                        rel_coordinate = relative(
                            coordinates, (obj.rect[0], obj.rect[1])
                        )
                        # and \
                        #     (coordinates[0] < max_x
                        #      or coordinates[0] > min_x
                        #      or coordinates[1] < max_y
                        #      or coordinates[1] > min_y)
                        try:
                            while obj.mask.get_at(rel_coordinate):
                                coordinates = generate_coordinates(self.screen)
                                rel_coordinate = relative(
                                    coordinates, (obj.rect[0], obj.rect[1])
                                )
                        except IndexError:
                            pass
                            #print('-' * 50)
                            #print("ERR", IndexError)
                            #print('-' * 50)
                    # print(coordinates, index)
                    self.add_agent(Person(pos=np.array(coordinates),
                                          v=None, population=self, index=index))
