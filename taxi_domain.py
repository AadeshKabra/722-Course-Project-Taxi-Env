"""
GTPyhop domain definition for Taxi-v3 environment
Defines operators (primitive actions), task methods, and state representation
Compatible with GTPyhop version 1.4.0
"""

import gtpyhop
import copy
from collections import deque

# ============================================
# DOMAIN CREATION - MUST BE FIRST!
# ============================================

# Create the domain object (required before any declarations)
gtpyhop.current_domain = gtpyhop.Domain('taxi')


# ============================================
# STATE REPRESENTATION
# ============================================

def make_state(taxi_pos, passenger_loc, destination, passenger_in_taxi=False):
    """
    Create a GTPyhop state for Taxi

    Args:
        taxi_pos: (row, col) tuple for taxi position
        passenger_loc: (row, col) tuple or None if in taxi
        destination: (row, col) tuple for destination
        passenger_in_taxi: bool indicating if passenger is in taxi
    """
    state = gtpyhop.State('taxi_state')
    state.taxi_pos = taxi_pos
    state.passenger_loc = passenger_loc
    state.destination = destination
    state.passenger_in_taxi = passenger_in_taxi

    # Taxi-v3 wall configuration
    state.walls = {
        # Top-left vertical wall (between columns 0-1, rows 0-1)
        ((0, 0), (0, 1)), ((0, 1), (0, 0)),
        ((1, 0), (1, 1)), ((1, 1), (1, 0)),
        # Top-right vertical wall (between columns 3-4, rows 0-1)
        ((0, 3), (0, 4)), ((0, 4), (0, 3)),
        ((1, 3), (1, 4)), ((1, 4), (1, 3)),
        # Bottom-left L-shaped wall
        ((3, 0), (4, 0)), ((4, 0), (3, 0)),  # Horizontal part
        ((3, 0), (3, 1)), ((3, 1), (3, 0)),  # Vertical part row 3
        ((4, 0), (4, 1)), ((4, 1), (4, 0)),  # Vertical part row 4
        # Bottom-middle reverse-L shaped wall
        ((3, 2), (4, 2)), ((4, 2), (3, 2)),  # Horizontal part
        ((3, 2), (3, 3)), ((3, 3), (3, 2)),  # Vertical part row 3
        ((4, 2), (4, 3)), ((4, 3), (4, 2)),  # Vertical part row 4
    }

    return state


# ============================================
# OPERATORS (Primitive Actions) - WITH PROPER STATE COPYING
# ============================================

def move_north(state):
    """Move taxi one cell north if no wall blocks the path"""
    row, col = state.taxi_pos
    new_pos = (row - 1, col)

    # Check boundaries
    if row <= 0:
        return False

    # Check walls
    if (state.taxi_pos, new_pos) in state.walls:
        return False

    # Create NEW state (immutable state transitions)
    new_state = copy.deepcopy(state)
    new_state.taxi_pos = new_pos
    return new_state


def move_south(state):
    """Move taxi one cell south if no wall blocks the path"""
    row, col = state.taxi_pos
    new_pos = (row + 1, col)

    if row >= 4:
        return False

    if (state.taxi_pos, new_pos) in state.walls:
        return False

    # Create NEW state
    new_state = copy.deepcopy(state)
    new_state.taxi_pos = new_pos
    return new_state


def move_east(state):
    """Move taxi one cell east if no wall blocks the path"""
    row, col = state.taxi_pos
    new_pos = (row, col + 1)

    if col >= 4:
        return False

    if (state.taxi_pos, new_pos) in state.walls:
        return False

    # Create NEW state
    new_state = copy.deepcopy(state)
    new_state.taxi_pos = new_pos
    return new_state


def move_west(state):
    """Move taxi one cell west if no wall blocks the path"""
    row, col = state.taxi_pos
    new_pos = (row, col - 1)

    if col <= 0:
        return False

    if (state.taxi_pos, new_pos) in state.walls:
        return False

    # Create NEW state
    new_state = copy.deepcopy(state)
    new_state.taxi_pos = new_pos
    return new_state


def pickup_passenger(state):
    """Pick up passenger if taxi is at passenger location"""
    # Preconditions
    if state.passenger_in_taxi:
        return False  # Already have passenger

    if state.passenger_loc is None:
        return False  # No passenger to pick up

    if state.taxi_pos != state.passenger_loc:
        return False  # Not at passenger location

    # Create NEW state with effects
    new_state = copy.deepcopy(state)
    new_state.passenger_in_taxi = True
    new_state.passenger_loc = None
    return new_state


def dropoff_passenger(state):
    """Drop off passenger if taxi is at destination"""
    # Preconditions
    if not state.passenger_in_taxi:
        return False  # No passenger to drop off

    if state.taxi_pos != state.destination:
        return False  # Not at destination

    # Create NEW state with effects
    new_state = copy.deepcopy(state)
    new_state.passenger_in_taxi = False
    new_state.passenger_loc = state.taxi_pos
    return new_state


# ============================================
# PATHFINDING HELPER
# ============================================

def bfs_pathfind(start, goal, walls):
    """
    BFS pathfinding that respects walls in Taxi-v3

    Args:
        start: (row, col) starting position
        goal: (row, col) goal position
        walls: set of ((r1,c1), (r2,c2)) tuples representing walls

    Returns:
        List of (row, col) positions from start to goal, or None if no path
    """
    if start == goal:
        return [start]

    # Queue: (position, path)
    queue = deque([(start, [start])])
    visited = {start}

    while queue:
        (row, col), path = queue.popleft()

        # Try all four directions
        for dr, dc in [(-1, 0), (1, 0), (0, 1), (0, -1)]:
            new_row, new_col = row + dr, col + dc
            new_pos = (new_row, new_col)

            # Check boundaries
            if not (0 <= new_row <= 4 and 0 <= new_col <= 4):
                continue

            # Check if already visited
            if new_pos in visited:
                continue

            # Check walls
            if ((row, col), new_pos) in walls:
                continue

            # Found goal
            if new_pos == goal:
                return path + [new_pos]

            # Add to queue
            visited.add(new_pos)
            queue.append((new_pos, path + [new_pos]))

    # No path found
    return None


# ============================================
# TASK METHODS
# ============================================

def m_transport_with_passenger(state):
    """
    Method for 'transport' task when passenger is already in taxi
    Task: ('transport',)
    Precondition: passenger_in_taxi == True
    Subtasks: navigate to destination, drop off
    """
    if state.passenger_in_taxi:
        return [
            ('navigate', state.destination),
            ('dropoff_passenger',)
        ]
    return False


def m_transport_without_passenger(state):
    """
    Method for 'transport' task when passenger needs to be picked up
    Task: ('transport',)
    Precondition: passenger_in_taxi == False
    Subtasks: get passenger, deliver passenger
    """
    if not state.passenger_in_taxi and state.passenger_loc is not None:
        return [
            ('get_passenger',),
            ('deliver_passenger',)
        ]
    return False


def m_get_passenger(state):
    """
    Method for 'get_passenger' task
    Task: ('get_passenger',)
    Subtasks: navigate to passenger, pick up
    """
    if state.passenger_loc is None:
        return False

    return [
        ('navigate', state.passenger_loc),
        ('pickup_passenger',)
    ]


def m_deliver_passenger(state):
    """
    Method for 'deliver_passenger' task
    Task: ('deliver_passenger',)
    Subtasks: navigate to destination, drop off
    """
    return [
        ('navigate', state.destination),
        ('dropoff_passenger',)
    ]


def m_navigate_to_location(state, target_location):
    """
    Method for 'navigate' task using BFS pathfinding that respects walls
    Task: ('navigate', target_location)
    Subtasks: sequence of movement actions

    Uses BFS to find shortest path avoiding walls
    """
    current = state.taxi_pos
    target = target_location

    # Already at target
    if current == target:
        return []

    # BFS to find shortest path
    path = bfs_pathfind(current, target, state.walls)

    if not path:
        # No valid path found
        return False

    # Convert path to movement actions
    actions = []
    for i in range(len(path) - 1):
        current_pos = path[i]
        next_pos = path[i + 1]

        # Determine direction of movement
        row_diff = next_pos[0] - current_pos[0]
        col_diff = next_pos[1] - current_pos[1]

        if row_diff == -1:
            actions.append(('move_north',))
        elif row_diff == 1:
            actions.append(('move_south',))
        elif col_diff == 1:
            actions.append(('move_east',))
        elif col_diff == -1:
            actions.append(('move_west',))

    return actions


# ============================================
# DOMAIN INITIALIZATION
# ============================================

def initialize_domain():
    """
    Initialize GTPyhop domain for Taxi-v3
    This function declares all actions and task methods
    """
    # Declare all actions (operators)
    gtpyhop.declare_actions(
        move_north, move_south, move_east, move_west,
        pickup_passenger, dropoff_passenger
    )

    # Declare task methods
    gtpyhop.declare_task_methods('transport',
                                  m_transport_with_passenger,
                                  m_transport_without_passenger)
    gtpyhop.declare_task_methods('navigate',
                                  m_navigate_to_location)
    gtpyhop.declare_task_methods('get_passenger',
                                  m_get_passenger)
    gtpyhop.declare_task_methods('deliver_passenger',
                                  m_deliver_passenger)

    print("✓ Taxi HTN domain initialized successfully")


# ============================================
# HELPER FUNCTIONS
# ============================================

def decode_gym_obs(env, obs):
    """
    Convert Gym Taxi-v3 observation to GTPyhop state

    Args:
        env: Gymnasium Taxi-v3 environment
        obs: Integer observation from environment

    Returns:
        GTPyhop state object
    """
    LOCATIONS = {'R': (0, 0), 'G': (0, 4), 'Y': (4, 0), 'B': (4, 3)}
    LOC_NAMES = ['R', 'G', 'Y', 'B']

    taxi_row, taxi_col, pass_idx, dest_idx = env.unwrapped.decode(obs)

    taxi_pos = (taxi_row, taxi_col)

    if pass_idx == 4:  # Passenger in taxi
        passenger_loc = None
        passenger_in_taxi = True
    else:
        pr, pc = LOCATIONS[LOC_NAMES[pass_idx]]
        passenger_loc = (pr, pc)
        passenger_in_taxi = False

    dr, dc = LOCATIONS[LOC_NAMES[dest_idx]]
    destination = (dr, dc)

    return make_state(taxi_pos, passenger_loc, destination, passenger_in_taxi)


def action_to_gym(action_name):
    """
    Convert GTPyhop action name to Gym action integer

    Args:
        action_name: String name of action (e.g., 'move_north')

    Returns:
        Integer Gym action (0-5)
    """
    ACTION_MAP = {
        'move_north': 1,
        'move_south': 0,
        'move_east': 2,
        'move_west': 3,
        'pickup_passenger': 4,
        'dropoff_passenger': 5
    }

    # Handle both string and tuple formats
    if isinstance(action_name, tuple):
        action_name = action_name[0]

    return ACTION_MAP.get(action_name, 0)
