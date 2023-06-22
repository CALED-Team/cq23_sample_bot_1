from abc import ABC, abstractmethod

import comms
from object_types import ObjectTypes


class GameState:
    def __init__(self, tank_id):
        self.tank_id = tank_id
        self.our_tank = None
        self.opp_tank = None

        # Assuming that there's only ever going to be 1 game boundary and 1
        # closing boundary...
        self.boundary = None
        self.closing_boundary = None

        self.containers = {
            ObjectTypes.BULLET: {},
            ObjectTypes.WALL: {},
            ObjectTypes.DESTRUCTIBLE_WALL: {},
            ObjectTypes.POWERUP: {},
        }

    def update_state(self, key, val):
        """Updates the state of an object in the game."""
        match ObjectTypes(val["type"]):
            case ObjectTypes.TANK:
                if key == self.tank_id:
                    self.our_tank = val
                else:
                    self.opp_tank = val
            case ObjectTypes.BOUNDARY:
                self.boundary = val
            case ObjectTypes.CLOSING_BOUNDARY:
                self.closing_boundary = val
            case other:
                self.containers[other].update({key: val})

    def delete_objs(self, key):
        """Remove an object from the game state."""
        for val in self.containers.values():
            if key in val:
                del val[key]


class Strategy(ABC):
    def __init__(self):
        self.tank_id = comms.read_message()["message"]["your-tank-id"]
        self.game_state = GameState(self.tank_id)

        self.current_turn_message = None

        while (next_init_message := comms.read_message()) != comms.END_INIT_SIGNAL:
            for key, val in next_init_message["message"]["updated_objects"].items():
                self.game_state.update_state(key, val)

    def read_next_turn_data(self):
        self.current_turn_message = comms.read_message()

        if self.current_turn_message == comms.END_SIGNAL:
            return False

        for key, val in self.current_turn_message["message"]["updated_objects"].items():
            self.game_state.update_state(key, val)

        for key in self.current_turn_message["message"]["deleted_objects"]:
            self.game_state.delete_objs(key)

        return True

    @abstractmethod
    def respond_to_turn(self):
        pass
