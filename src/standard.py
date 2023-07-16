import math
import sys

import comms
from object_types import ObjectTypes
from strategy import Strategy

BULLET_VELOCITY = 450


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

        target_time = 0

        # Don't fire if the target is too far away.
        while target_time < 5:
            # Update positions.
            x1, x2 = position_prediction(
                [x1, x2], self.game_state.our_tank["velocity"], target_time
            )
            x2, y2 = position_prediction(
                [x2, y2], self.game_state.opp_tank["velocity"], target_time)

            # Calculate the angle the bullet needs to be fired at.
            theta = math.atan2(y2 - y1, x2 - x1) * 180 / math.pi

            # Time it will take for the bullet to reach our opponent.
            t = x2 / (math.cos(theta) / BULLET_VELOCITY)

            if t < target_time:
                actions.update({"shoot": theta})
                break

            target_time += 0.01

        if actions:
            comms.post_message(actions)


def position_prediction(p, v, t):
    """
    Returns the predicated position of a point p with the directional
    velocity v in t time.
    """
    return [p[0] + v[0] * t, p[1] + v[1] * t]


def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + (p1[1] - p2[1])
