from collections import deque
from dataclasses import dataclass, field


MODE_1 = "Sensorless Search"
MODE_AND_OR = "AND-OR Search"
MODE_3 = "Partially Observable"


@dataclass
class WorldState:
    grid: list
    actual_position: tuple
    goal_position: tuple
    start_position: tuple


@dataclass
class Observation:
    mode: str
    grid: list
    start_position: tuple | None = None
    actual_position: tuple | None = None
    goal_position: tuple | None = None
    fog_mask: set = field(default_factory=set)
    visible_positions: set = field(default_factory=set)


class BeliefState:
    """Generic belief container used for Steve or Goal candidates."""

    def __init__(self, positions=None, label="steve"):
        self.label = label
        self.positions = set()
        self.probabilities = {}
        if positions is not None:
            self.initialize(positions)

    def initialize(self, positions):
        positions = [tuple(pos) for pos in positions]
        self.positions = set(positions)
        if self.positions:
            probability = 1.0 / len(self.positions)
            self.probabilities = {
                pos: probability for pos in self.positions
            }
        else:
            self.probabilities = {}
        return self

    def update(self, positions):
        return self.initialize(positions)

    def remove(self, position):
        if position in self.positions:
            self.positions.remove(position)
            if self.positions:
                probability = 1.0 / len(self.positions)
                self.probabilities = {
                    pos: probability for pos in self.positions
                }
            else:
                self.probabilities = {}
        return self

    def belief_size(self):
        return len(self.positions)

    def entropy(self):
        return 0.0


class TransitionModel:
    """Deterministic grid transition model."""

    def next_position(self, position, action):
        row, col = position
        if action == "up":
            return row - 1, col
        if action == "down":
            return row + 1, col
        if action == "left":
            return row, col - 1
        return row, col + 1

    def is_walkable(self, grid, position):
        row, col = position
        if not (0 <= row < len(grid) and 0 <= col < len(grid[0])):
            return False
        return grid[row][col] != 4

    def move(self, grid, position, action):
        next_pos = self.next_position(position, action)
        if self.is_walkable(grid, next_pos):
            return next_pos
        return position

    def propagate_belief(self, grid, positions, action):
        next_positions = set()
        for position in positions:
            next_positions.add(self.move(grid, position, action))
        return next_positions


class ANDORProblem:
    """Deterministic search problem used by the AND-OR planner."""

    def __init__(self, grid, initial_state, goal_state, transition_model, visited_positions=None):
        self.grid = grid
        self.initial_state = initial_state
        self.goal_state = goal_state
        self.transition_model = transition_model
        self.visited_positions = set(visited_positions or [])
        self.expanded_nodes = 0

    def goal_test(self, state):
        return state == self.goal_state

    def actions(self, state):
        actions = []
        for action in ["up", "down", "left", "right"]:
            nxt = self.transition_model.move(self.grid, state, action)
            if nxt != state and (nxt not in self.visited_positions or nxt == self.goal_state):
                actions.append(action)
        actions.sort(
            key=lambda action: (
                self.manhattan(self.transition_model.move(self.grid, state, action), self.goal_state),
                action,
            )
        )
        return actions

    def results(self, state, action):
        nxt = self.transition_model.move(self.grid, state, action)
        if nxt == state:
            return []
        return [nxt]

    def manhattan(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])


class ObservationModel:
    """Returns only the information allowed by the current mode."""

    def observe(self, world_state, mode, visibility_state=None):
        grid = self._copy_grid(world_state.grid)

        if mode == MODE_1:
            self._hide_cell(grid, world_state.start_position, blank=0)
            visible_positions = self._visible_positions(grid)
            return Observation(
                mode=mode,
                grid=grid,
                goal_position=world_state.goal_position,
                visible_positions=visible_positions
            )

        if mode == MODE_AND_OR:
            visible_positions = self._visible_positions(grid)
            return Observation(
                mode=mode,
                grid=grid,
                start_position=world_state.start_position,
                actual_position=world_state.actual_position,
                visible_positions=visible_positions
            )

        fog_mask = set()
        if visibility_state is not None:
            fog_mask = set(visibility_state.active_mask())

        for position in fog_mask:
            self._hide_cell(grid, position, blank=None)

        visible_positions = self._visible_positions(grid)
        return Observation(
            mode=mode,
            grid=grid,
            start_position=world_state.start_position,
            actual_position=world_state.actual_position,
            goal_position=world_state.goal_position if world_state.goal_position not in fog_mask else None,
            fog_mask=fog_mask,
            visible_positions=visible_positions
        )

    def _copy_grid(self, grid):
        return [row[:] for row in grid]

    def _hide_cell(self, grid, position, blank=None):
        if position is None:
            return
        row, col = position
        grid[row][col] = blank

    def _visible_positions(self, grid):
        positions = set()
        for row in range(len(grid)):
            for col in range(len(grid[0])):
                if grid[row][col] is not None:
                    positions.add((row, col))
        return positions


class VisibilityState:
    """Tracks which cells of the fog region have been revealed."""

    def __init__(self, fog_radius=2, reveal_radius=1):
        self.fog_radius = fog_radius
        self.reveal_radius = reveal_radius
        self.base_mask = set()
        self.revealed = set()

    def initialize(self, goal_position, rows, cols):
        self.base_mask = set()
        goal_row, goal_col = goal_position

        for row in range(rows):
            for col in range(cols):
                distance = abs(row - goal_row) + abs(col - goal_col)
                if distance <= self.fog_radius:
                    self.base_mask.add((row, col))

        self.revealed = set()
        return self

    def active_mask(self):
        return self.base_mask - self.revealed

    def reveal_from_position(self, position):
        if position is None:
            return self

        row, col = position
        newly_revealed = set()

        for candidate in self.base_mask:
            if abs(candidate[0] - row) + abs(candidate[1] - col) <= self.reveal_radius:
                newly_revealed.add(candidate)

        self.revealed |= newly_revealed
        return self


class Level4Planner:
    """Mode-aware planner that only consumes observation + belief."""

    def __init__(self, transition_model):
        self.transition_model = transition_model

    def next_action(self, observation, belief, goal_position=None, visited_positions=None):
        if observation.mode == MODE_1:
            return self._plan_mode1(observation, belief)
        if observation.mode == MODE_AND_OR:
            return self._plan_and_or(observation, belief, goal_position, visited_positions)
        return self._plan_mode3(observation, belief)

    def _plan_mode1(self, observation, belief):
        if belief.belief_size() == 0 or observation.goal_position is None:
            return None, 0

        best_action = None
        best_score = None
        expanded = 0
        actions = ["up", "down", "left", "right"]

        for action in actions:
            expanded += len(belief.positions)
            next_positions = self.transition_model.propagate_belief(
                observation.grid,
                belief.positions,
                action
            )
            if not next_positions:
                continue

            score = max(
                abs(row - observation.goal_position[0]) +
                abs(col - observation.goal_position[1])
                for row, col in next_positions
            )

            if best_score is None or score < best_score or (
                score == best_score and action < best_action
            ):
                best_score = score
                best_action = action

        return best_action, expanded

    def _plan_and_or(self, observation, belief, goal_position=None, visited_positions=None):
        if observation.actual_position is None or goal_position is None:
            return None, 0

        problem = ANDORProblem(
            grid=observation.grid,
            initial_state=observation.actual_position,
            goal_state=goal_position,
            transition_model=self.transition_model,
            visited_positions=visited_positions
        )

        plan, expanded = self.and_or_graph_search(problem)
        if plan is None:
            return None, expanded

        return self._first_action_from_plan(plan), expanded

    def _normalize_plan(self, plan):
        if plan is None:
            return None
        if isinstance(plan, list):
            return [self._normalize_plan(item) for item in plan]
        if isinstance(plan, dict):
            return {state: self._normalize_plan(subplan) for state, subplan in plan.items()}
        return plan

    def and_or_graph_search(self, problem):
        plan = self._or_search(problem.initial_state, problem, [])
        return plan, problem.expanded_nodes

    def _or_search(self, state, problem, path):
        problem.expanded_nodes += 1

        if problem.goal_test(state):
            return []

        if state in path:
            return None

        for action in problem.actions(state):
            result_states = problem.results(state, action)
            plan = self._and_search(result_states, problem, path + [state])
            if plan is not None:
                return [action, plan]

        return None

    def _and_search(self, states, problem, path):
        plans = {}
        for state in states:
            plan_s = self._or_search(state, problem, path)
            if plan_s is None:
                return None
            plans[state] = plan_s
        return plans

    def _first_action_from_plan(self, plan):
        if not plan:
            return None
        if isinstance(plan, list):
            return plan[0] if plan else None
        return None

    def _plan_mode3(self, observation, belief):
        if observation.actual_position is None:
            return None, 0

        if observation.goal_position is not None:
            return self._shortest_action_to_targets(
                observation.grid,
                observation.actual_position,
                {observation.goal_position},
                allow_unknown=False
            )

        fog_frontier = self._fog_frontier_targets(
            observation.grid,
            belief.positions,
            observation.actual_position
        )

        if fog_frontier:
            return self._shortest_action_to_targets(
                observation.grid,
                observation.actual_position,
                fog_frontier,
                allow_unknown=False
            )

        remaining = set(belief.positions)
        remaining.discard(observation.actual_position)

        if not remaining:
            return None, 0

        return self._shortest_action_to_targets(
            observation.grid,
            observation.actual_position,
            remaining,
            allow_unknown=False
        )

    def _shortest_action_to_targets(self, grid, start, targets, allow_unknown=False):
        if start in targets:
            return None, 0

        queue = deque([start])
        parents = {start: None}
        actions = ["up", "down", "left", "right"]
        expanded = 0

        while queue:
            current = queue.popleft()
            expanded += 1

            for action in actions:
                nxt = self.transition_model.next_position(current, action)
                if nxt in parents:
                    continue

                if not allow_unknown and not self.transition_model.is_walkable(grid, nxt):
                    continue

                if allow_unknown and not self.transition_model.is_walkable(grid, nxt):
                    continue

                parents[nxt] = (current, action)
                if nxt in targets:
                    return self._recover_first_action(parents, start, nxt), expanded
                queue.append(nxt)

        return None, expanded

    def _recover_first_action(self, parents, start, end):
        current = end
        while current != start:
            parent, action = parents[current]
            if parent == start:
                return action
            current = parent
        return None

    def _fog_frontier_targets(self, grid, fog_positions, actual_position):
        if not fog_positions:
            return set()

        targets = set()
        for row, col in fog_positions:
            for action in ["up", "down", "left", "right"]:
                neighbor = self.transition_model.next_position((row, col), action)
                if neighbor == actual_position:
                    continue
                if self.transition_model.is_walkable(grid, neighbor) and neighbor not in fog_positions:
                    targets.add(neighbor)
        return targets
