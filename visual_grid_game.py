# visual_grid_game.py
import random
import tkinter as tk

DIRECTION_VECTORS = {
    'Up': (0, 1),
    'Down': (0, -1),
    'Left': (-1, 0),
    'Right': (1, 0)
}


class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]  # Starting position (x, y)
        self.agent_direction = 'Right'

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            # Generate some default scattered walls for a larger grid
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}

        # Dynamically generate random food positions avoiding walls and agent start
        self.food_positions = set()
        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            pos_tuple = (fx, fy)
            if pos_tuple != (0, 0) and pos_tuple not in self.walls:
                self.food_positions.add(pos_tuple)

        # Generate adversarial opponents
        self.opponents = []
        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)
            op_pos = [ox, oy]
            if tuple(op_pos) != (0, 0) and tuple(op_pos) not in self.walls and tuple(op_pos) not in self.food_positions:
                self.opponents.append(op_pos)


        # Generate toxic trap positions
        self.toxic_traps = set()

        while len(self.toxic_traps) < 3:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)
            trap_position = (tx, ty)

            if (
                trap_position != (0, 0)
                and trap_position not in self.walls
                and trap_position not in self.food_positions
                and trap_position not in [tuple(opponent) for opponent in self.opponents]
            ):
                self.toxic_traps.add(trap_position)

        self.score = 0
        self.steps = 0
        self.collision = False


    def get_cell_ahead(self):
        dx, dy = DIRECTION_VECTORS[self.agent_direction]

        return (
            self.agent_pos[0] + dx,
            self.agent_pos[1] + dy
        )  


    def is_blocked(self, position):
        x, y = position

        outside_grid = (
            x < 0 or
            x >= self.width or
            y < 0 or
            y >= self.height
        )

        return outside_grid or position in self.walls  

    def get_percept(self):
        cell_ahead = self.get_cell_ahead()

        return {
            'wall_ahead': self.is_blocked(cell_ahead),

            'food_here':
                tuple(self.agent_pos) in self.food_positions,

            'smells_toxin':
                tuple(self.agent_pos) in self.toxic_traps,

            'collision': self.collision
        }

    def execute_action(self, action):
        self.steps += 1

        if action == 'Suck':

            current_pos = tuple(self.agent_pos)

            if current_pos in self.food_positions:
                self.food_positions.remove(current_pos)
                self.score += 20

        elif action == 'TurnLeft':

            directions = ['Up', 'Left', 'Down', 'Right']

            current_index = directions.index(
                self.agent_direction
            )

            self.agent_direction = directions[
                (current_index + 1) % 4
            ]

        elif action == 'TurnRight':

            directions = ['Up', 'Right', 'Down', 'Left']

            current_index = directions.index(
                self.agent_direction
            )

            self.agent_direction = directions[
                (current_index + 1) % 4
            ]

        elif action == 'MoveForward':

            new_pos = self.get_cell_ahead()

            if self.is_blocked(new_pos):
                self.score -= 5

            else:
                self.agent_pos = [
                    new_pos[0],
                    new_pos[1]
                ]

                # Lab 1: toxic-trap penalty
                if tuple(self.agent_pos) in self.toxic_traps:
                    self.score -= 15

        # Preserve opponent movement from the original environment
        for op in self.opponents:
            move = random.choice([
                'Up',
                'Down',
                'Left',
                'Right',
                'Stay'
            ])

            if move == 'Up' and op[1] < self.height - 1:
                candidate = (op[0], op[1] + 1)
                if candidate not in self.walls:
                    op[1] += 1

            elif move == 'Down' and op[1] > 0:
                candidate = (op[0], op[1] - 1)
                if candidate not in self.walls:
                    op[1] -= 1

            elif move == 'Left' and op[0] > 0:
                candidate = (op[0] - 1, op[1])
                if candidate not in self.walls:
                    op[0] -= 1

            elif move == 'Right' and op[0] < self.width - 1:
                candidate = (op[0] + 1, op[1])
                if candidate not in self.walls:
                    op[0] += 1

            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision

class SimpleReflexAgent:

    def sense_and_act(self, percept):

        if percept['food_here']:
            return 'Suck'

        if percept['wall_ahead']:
            return 'TurnLeft'

        return 'MoveForward'    

class ModelBasedAgent:

    def __init__(self):
        self.estimated_pos = (0, 0)
        self.estimated_direction = 'Right'

        self.visited_cells = {(0, 0)}

        self.last_action = None


    def get_left_direction(self):

        directions = ['Up', 'Right', 'Down', 'Left']

        current_index = directions.index(
            self.estimated_direction
        )

        return directions[
            (current_index - 1) % 4
        ]


    def get_right_direction(self):

        directions = ['Up', 'Right', 'Down', 'Left']

        current_index = directions.index(
            self.estimated_direction
        )

        return directions[
            (current_index + 1) % 4
        ]


    def get_relative_cell(self, direction):

        dx, dy = DIRECTION_VECTORS[direction]

        return (
            self.estimated_pos[0] + dx,
            self.estimated_pos[1] + dy
        )

    def update_state(self):

        if self.last_action == 'TurnLeft':

            self.estimated_direction = (
                self.get_left_direction()
            )

        elif self.last_action == 'TurnRight':

            self.estimated_direction = (
                self.get_right_direction()
            )

        elif self.last_action == 'MoveForward':

            self.estimated_pos = (
                self.get_relative_cell(
                    self.estimated_direction
                )
            )

        self.visited_cells.add(
            self.estimated_pos
        )

    def sense_and_act(self, percept):

        self.update_state()

        if percept['food_here']:
            action = 'Suck'

        else:

            ahead = self.get_relative_cell(
                self.estimated_direction
            )

            left_direction = (
                self.get_left_direction()
            )

            right_direction = (
                self.get_right_direction()
            )

            left_cell = self.get_relative_cell(
                left_direction
            )

            right_cell = self.get_relative_cell(
                right_direction
            )

            if percept['wall_ahead']:

                if left_cell not in self.visited_cells:
                    action = 'TurnLeft'

                elif right_cell not in self.visited_cells:
                    action = 'TurnRight'

                else:
                    action = 'TurnRight'

            elif ahead in self.visited_cells:

                if left_cell not in self.visited_cells:
                    action = 'TurnLeft'

                else:
                    action = 'TurnRight'

            else:
                action = 'MoveForward'

        self.last_action = action

        return action

class GridGameGUI:
    """Tkinter wrapper that dynamically scales cell sizes to keep larger grids on screen."""

    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, walls=None, agent_type='model'):
        self.root = root

        self.env = VisualGridHuntGame(width=width, height=height, num_food=num_food, num_opponents=num_opponents,
                                      custom_walls=walls)

        # Easy switch between the two Lab 2 agents
        if agent_type == 'simple':
            self.agent = SimpleReflexAgent()
            self.agent_name = 'Simple Reflex Agent'
        elif agent_type == 'model':
            self.agent = ModelBasedAgent()
            self.agent_name = 'Model-Based Agent'
        else:
            raise ValueError("agent_type must be 'simple' or 'model'")

        self.root.title(f"IT3012 - {self.agent_name}")

        # Dynamically calculate cell size so the total canvas fits nicely within a 600x600 window ceiling
        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height))

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(root, text=f"{self.agent_name} | Score: 0 | Steps: 0", font=("Arial", 14))
        self.label.pack(pady=10)

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 12), bg="#000066",
                             fg="white")
        self.btn.pack(pady=5)

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")

        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cbd5e1")

                # Only draw text if cell is large enough
                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(x1 + self.cell_size / 2, y1 + self.cell_size / 2, text="W", fill="white",
                                            font=("Arial", 8, "bold"))

        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#f59e0b",
                                    outline="#d97706")

        # Draw toxic traps as purple triangles
        for tx, ty in self.env.toxic_traps:
            x1 = tx * self.cell_size
            y1 = (self.env.height - 1 - ty) * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size

            self.canvas.create_polygon(
                x1 + self.cell_size * 0.5,
                y1 + self.cell_size * 0.15,

                x1 + self.cell_size * 0.85,
                y1 + self.cell_size * 0.85,

                x1 + self.cell_size * 0.15,
                y1 + self.cell_size * 0.85,

                fill="#9333ea",
                outline="#581c87",
                width=2
            )

        for ox, oy in self.env.opponents:
            offset = self.cell_size * 0.2
            x1 = ox * self.cell_size + offset
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6, fill="#990000",
                                         outline="#7a0000")

        ax, ay = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
        self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7, fill="#000066",
                                outline="#1e3a8a")

        # Show the direction the agent is currently facing
        direction_symbols = {
            'Up': '↑',
            'Down': '↓',
            'Left': '←',
            'Right': '→'
        }

        self.canvas.create_text(
            x1 + self.cell_size * 0.35,
            y1 + self.cell_size * 0.35,
            text=direction_symbols[self.env.agent_direction],
            fill="white",
            font=("Arial", max(10, self.cell_size // 3), "bold")
        )

    def run_loop(self):
        self.btn.config(state="disabled")

        def step():
            if not self.env.is_done():
                percept = self.env.get_percept()

                action = self.agent.sense_and_act(percept)

                self.env.execute_action(action)

                self.draw_grid()
                self.label.config(
                    text=(
                        f"{self.agent_name} | Score: {self.env.score} | "
                        f"Steps: {self.env.steps} | "
                        f"Action: {action} | "
                        f"Percept: {percept}"
                    )
                )

                self.root.after(250, step)

            else:
                end_text = (
                    f"{self.agent_name} Finished! Final Score: {self.env.score} | "
                    f"Steps: {self.env.steps}"
                )

                self.label.config(text=end_text)
                self.btn.config(state="normal")

        step()


if __name__ == "__main__":
    # Keep the same random layout when comparing the two agents.
    random.seed(42)

    # Change only this value when testing:
    # 'simple' -> Simple Reflex Agent
    # 'model'  -> Model-Based Agent
    AGENT_TYPE = 'model'

    root = tk.Tk()

    app = GridGameGUI(
        root,
        width=12,
        height=12,
        num_food=15,
        num_opponents=0,
        agent_type=AGENT_TYPE
    )

    root.mainloop()
