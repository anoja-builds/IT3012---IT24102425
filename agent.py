# agent.py
import math
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
        self.active_algo = 'AStar'

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


    def dfs_search(
        self,
        start,
        target,
        grid_size,
        walls
    ):

        frontier = [
            (start, [])
        ]

        reached = {start}

        actions = [
            'MoveForward',
            'TurnLeft',
            'TurnRight'
        ]

        while frontier:

            # DFS uses a LIFO stack
            state, path = frontier.pop()

            x, y, direction = state

            # Goal test
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


    def ucs_search(
        self,
        start,
        target,
        grid_size,
        walls
    ):

        frontier = []

        counter = 0

        heapq.heappush(
            frontier,
            (
                0,
                counter,
                start,
                []
            )
        )

        reached = set()

        actions = [
            'MoveForward',
            'TurnLeft',
            'TurnRight'
        ]

        while frontier:

            cost, _, state, path = heapq.heappop(
                frontier
            )

            if state in reached:
                continue

            reached.add(state)

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
                    and next_state not in reached
                ):

                    new_cost = cost + 1
                    new_path = path + [action]

                    counter += 1

                    heapq.heappush(
                        frontier,
                        (
                            new_cost,
                            counter,
                            next_state,
                            new_path
                        )
                    )

        return []


    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        heuristic_type='manhattan'
    ):
        frontier = []
        reached_states = set()

        actions = [
            'MoveForward',
            'TurnLeft',
            'TurnRight'
        ]

        # Starting position without direction
        start_xy = (
            start_pos[0],
            start_pos[1]
        )

        # Calculate starting heuristic h(n)
        if heuristic_type == 'euclidean':
            h_cost = self.euclidean_distance(
                start_xy,
                goal_pos
            )
        else:
            h_cost = self.manhattan_distance(
                start_xy,
                goal_pos
            )

        # Starting g(n) and f(n)
        g_cost = 0
        f_cost = g_cost + h_cost

        # Add starting state to priority queue
        heapq.heappush(
            frontier,
            (
                f_cost,
                g_cost,
                start_pos,
                []
            )
        )

        while frontier:
            (
                f_cost,
                g_cost,
                current_state,
                path_taken
            ) = heapq.heappop(frontier)

            # Skip already visited states
            if current_state in reached_states:
                continue

            current_x = current_state[0]
            current_y = current_state[1]

            # Check if goal reached
            if (current_x, current_y) == goal_pos:
                return path_taken

            reached_states.add(current_state)

            # Try possible actions
            for action in actions:
                next_state = self.get_next_state(
                    current_state,
                    action,
                    grid_size,
                    walls
                )

                if (
                    next_state is not None
                    and next_state not in reached_states
                ):
                    # New path cost
                    new_g_cost = g_cost + 1

                    next_xy = (
                        next_state[0],
                        next_state[1]
                    )

                    # New heuristic
                    if heuristic_type == 'euclidean':
                        new_h_cost = self.euclidean_distance(
                            next_xy,
                            goal_pos
                        )
                    else:
                        new_h_cost = self.manhattan_distance(
                            next_xy,
                            goal_pos
                        )

                    # f(n) = g(n) + h(n)
                    new_f_cost = new_g_cost + new_h_cost
                    new_path = path_taken + [action]

                    heapq.heappush(
                        frontier,
                        (
                            new_f_cost,
                            new_g_cost,
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

            if self.active_algo == 'BFS':

                self.plan = self.bfs_search(
                    start,
                    target,
                    grid_size,
                    walls
                )

            elif self.active_algo == 'DFS':

                self.plan = self.dfs_search(
                    start,
                    target,
                    grid_size,
                    walls
                )


            elif self.active_algo == 'UCS':

                self.plan = self.ucs_search(
                    start,
                    target,
                    grid_size,
                    walls
                )



            elif self.active_algo == 'AStar':
                self.plan = self.astar_search(
                    start,
                    target,
                    walls,
                    grid_size,
                    heuristic_type='manhattan'
                )

            print("Algorithm:", self.active_algo)
            print("Start:", start)
            print("Target:", target)
            print("Plan:", self.plan)

        if self.plan:
            return self.plan.pop(0)

        return 'TurnLeft'



    def manhattan_distance(self, pos, goal):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])


    def euclidean_distance(self, pos, goal):
        return math.sqrt(
            (pos[0] - goal[0]) ** 2
            + (pos[1] - goal[1]) ** 2
        )

if __name__ == "__main__":

    test_agent = SearchAgent()

    print(
        "Manhattan Distance:",
        test_agent.manhattan_distance((0, 0), (3, 4))
    )

    print(
        "Euclidean Distance:",
        test_agent.euclidean_distance((0, 0), (3, 4))
    )

    print("\nTesting A*:")

    plan = test_agent.astar_search(
        start_pos=(0, 0, 'Right'),
        goal_pos=(3, 0),
        walls=set(),
        grid_size=(5, 5),
        heuristic_type='manhattan'
    )

    print("A* Plan:", plan)
