import math
import sys

import comms
from object_types import ObjectTypes
from strategy import Strategy


class Standard(Strategy):
    """
    Standard Strategy:
    * Move towards the center of the closing boundary.
    * If there are powerups on the map, go for the closest one.
    * Shoot in the direction of our opponent.
    """

    def __init__(self):
        super().__init__()

        print("Standard Strategy Loaded!", file=sys.stderr)

        # Our current path goal.
        self.cur_goal = None

    def respond_to_turn(self):
        actions = {}

        if (
            self.cur_goal is None
            or self.game_state.our_tank["position"] == self.cur_goal
        ):
            # We've reached our goal, let's set a new one.
            if self.game_state.containers[ObjectTypes.POWERUP]:
                # At least one powerup is on the map, let's move to the closest.
                self.cur_goal = min(
                    (
                        pu["position"]
                        for pu in self.game_state.containers[
                            ObjectTypes.POWERUP
                        ].values()
                    ),
                    key=lambda p: manhattan_distance(
                        p, self.game_state.our_tank["position"]
                    ),
                )
            else:
                # No powerups, go the center of the map.
                x = max(x for x, _ in self.game_state.closing_boundary["position"])
                y = max(y for _, y in self.game_state.closing_boundary["position"])

                self.cur_goal = [x / 2, y / 2]

            # Queue up our next path action.
            actions.update({"path": self.cur_goal})

        # There's not much incentive to *not* shoot at our target, regardless
        # of if we have a clean line-of-sight.
        x1, y1 = self.game_state.our_tank["position"]
        x2, y2 = self.game_state.opp_tank["position"]
        theta = math.atan2(y2 - y1, x2 - x1) * 180 / math.pi

        actions.update({"shoot": theta})

        if actions:
            comms.post_message(actions)


def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + (p1[1] - p2[1])
