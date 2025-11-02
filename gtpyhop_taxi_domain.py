import gtpyhop


gtpyhop.Domain('taxi-htn')

class TaxiState(gtpyhop.State):
    def __init__(self, name):
        super().__init__(name)
        self.taxi_pos = {}
        self.passenger_pos = {}
        self.in_taxi = {}
        self.out_taxi = {}
        self.destinations = {}



def pickup_passenger(state, taxi, passenger, location):
    if(state.taxi_pos[taxi] == location and state.passenger_pos[passenger] == location and not state.in_taxi[passenger]):
        state.in_taxi[passenger] = True
        state.passenger_pos[passenger] = None
        return state

    return False


def dropoff_passenger(state, taxi, passenger, location):
    if(state.taxi_pos[taxi] == location and state.in_taxi[passenger] and state.destinations[passenger]==location):
        state.in_taxi[passenger] = False
        state.passenger_pos[passenger] = location
        return state

    return False


def move_north(state, taxi, origin, destination):
    if origin[0] - destination[0] == 1 and origin[1] == destination[1]:
        state.taxi_pos[taxi] = destination
        return state
    return False


def move_south(state, taxi, origin, destination):
    if destination[0] - origin[0] == 1 and origin[1] == destination[1]:
        state.taxi_pos[taxi] = destination
        return state
    return False


def move_east(state, taxi, origin, destination):
    if origin[0] == destination[0] and destination[1] - origin[1] == 1:
        state.taxi_pos[taxi] = destination
        return state
    return False


def move_west(state, taxi, origin, destination):
    if origin[0] == destination[0] and origin[1] - destination[1] == 1:
        state.taxi_pos[taxi] = destination
        return state
    return False


gtpyhop.declare_actions(pickup_passenger, dropoff_passenger, move_north, move_south, move_east, move_west)

def transport_passenger(state, taxi, passenger):
    passenger_loc = state.passenger_pos[passenger]
    goal_loc = state.destinations[passenger]
    return [
        ('move_to_location', taxi, passenger_loc),
        ('pickup_passenger', taxi, passenger),
        ('move_to_location', taxi, goal_loc),
        ('dropoff_passenger', taxi, passenger)
    ]


def move_to_location(state, taxi, destination):
    current = state.taxi_pos[taxi]
    if current == destination:
        return []

    moves = []
    x, y = current
    dx, dy = destination

    while x < dx:
        moves.append(('move_south', taxi, (x, y), (x+1, y)))
        x += 1

    while x > dx:
        moves.append(('move_north', taxi, (x, y), (x-1, y)))
        x -= 1

    while y < dy:
        moves.append(('move_east', taxi, (x, y), (x, y+1)))
        y += 1

    while y > dy:
        moves.append(('move_west', taxi, (x, y), (x, y-1)))
        y -= 1

    return moves


def m_deliver_passenger(state, passenger, location):
    passenger_loc = state.passenger_pos[passenger]
    if passenger_loc == location:
        return []

    return [('transport_passenger', 'taxi1', passenger)]


gtpyhop.declare_task_methods('transport_passenger', transport_passenger)
gtpyhop.declare_task_methods('move_to_location', move_to_location)
gtpyhop.declare_multigoal_methods('passenger_at', m_deliver_passenger)



state = TaxiState('test')
state.taxi_pos['taxi1'] = (0, 0)
state.passenger_pos['passenger1'] = (0, 4)
state.in_taxi['passenger1'] = False
state.destinations['passenger1'] = (4, 4)


gtpyhop.set_verbose_level(2)
plan = gtpyhop.find_plan(state, [('passenger_at', 'passenger1', (4, 4))])


if plan:
    for action in plan:
        print(action)

