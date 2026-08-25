# agent.py
import random
from collections import deque
import heapq

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)


DIRECTIONS = ['Up', 'Right', 'Down', 'Left']

DIRECTION_VECTORS = {
    'Up': (0, 1),
    'Right': (1, 0),
    'Down': (0, -1),
    'Left': (-1, 0)
}


class SearchAgent:

    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'

    def get_next_state(self, state, action, grid_size, walls):

        x, y, direction = state
        width, height = grid_size

        if action == 'TurnLeft':

            index = DIRECTIONS.index(direction)

            new_direction = DIRECTIONS[
                (index - 1) % 4
            ]

            return (x, y, new_direction)

        elif action == 'TurnRight':

            index = DIRECTIONS.index(direction)

            new_direction = DIRECTIONS[
                (index + 1) % 4
            ]

            return (x, y, new_direction)

        elif action == 'MoveForward':

            dx, dy = DIRECTION_VECTORS[direction]

            new_x = x + dx
            new_y = y + dy

            new_position = (new_x, new_y)

            inside_grid = (
                0 <= new_x < width and
                0 <= new_y < height
            )

            if (
                inside_grid and
                new_position not in walls
            ):
                return (
                    new_x,
                    new_y,
                    direction
                )

        return None

    def bfs_search(
        self,
        start,
        target,
        grid_size,
        walls
    ):

        frontier = deque()

        frontier.append(
            (start, [])
        )

        reached = {start}

        actions = [
            'MoveForward',
            'TurnLeft',
            'TurnRight'
        ]

        while frontier:

            state, path = frontier.popleft()

            x, y, direction = state

            if (x, y) == target:
                return path

            for action in actions:

                next_state = self.get_next_state(
                    state,
                    action,
                    grid_size,
                    walls
                )

                if (
                    next_state is not None
                    and
                    next_state not in reached
                ):

                    reached.add(next_state)

                    new_path = path + [action]

                    frontier.append(
                        (
                            next_state,
                            new_path
                        )
                    )

        return []


    def sense_and_act(self, percept):

        # Food underneath us -> collect it
        if percept['food_here']:
            self.plan = []
            return 'Suck'

        # No current plan -> build one
        if not self.plan:

            foods = percept['all_food']

            if not foods:
                return 'Suck'

            current_pos = percept['agent_pos']

            # Pick geometrically closest food
            target = min(
                foods,
                key=lambda food:
                    abs(food[0] - current_pos[0]) +
                    abs(food[1] - current_pos[1])
            )

            start = (
                current_pos[0],
                current_pos[1],
                percept['agent_direction']
            )

            grid_size = percept['grid_size']

            walls = set(
                percept['walls']
            )

            self.plan = self.bfs_search(
                start,
                target,
                grid_size,
                walls
            )

            print("Algorithm:", self.active_algo)
            print("Start:", start)
            print("Target:", target)
            print("Plan:", self.plan)

        if self.plan:
            return self.plan.pop(0)

        return 'TurnLeft'
