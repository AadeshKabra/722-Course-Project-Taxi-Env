import time
import os


def generate_locations(grid_size):
    locations = []
    for i in range(grid_size):
        for j in range(grid_size):
            locations.append(f"loc-{i}-{j}")

    return ' '.join(locations)


def generate_connections(grid_size):
    connections = []
    for i in range(grid_size):
        for j in range(grid_size):
            if j<grid_size - 1:
                connections.append(f"(east loc-{i}-{j} loc-{i}-{j + 1})")
                connections.append(f"(west loc-{i}-{j + 1} loc-{i}-{j})")

            if i < grid_size - 1:
                connections.append(f"(south loc-{i}-{j} loc-{i + 1}-{j})")
                connections.append(f"(north loc-{i + 1}-{j} loc-{i}-{j})")

    return '\n '.join(connections)


def problem_state(obs, problem_dir):
    taxi_pos = obs.taxi_pos
    passenger_pos = obs.passenger_pos
    goal_pos = obs.destination

    problem_content = f"""(define (problem taxi-problem-dynamic)
        (:domain taxi)
        (:objects
            {generate_locations(obs.grid_size)} - location
            taxi1 - taxi
            passenger1 - passenger
        )
        (:init
            (taxi-at taxi1 {taxi_pos})
            (passenger-at passenger1 {passenger_pos})
            (destination passenger1 {goal_pos})
            {generate_connections(obs.grid_size)}
        )
        (:goal (and
            (passenger-at passenger1 {goal_pos})
        ))
    )"""

    problem_file = os.path.join(problem_dir, 'dynamic_problem.pddl')
    with open(problem_file, 'w') as f:
        f.write(problem_content)

    return problem_file


def run_lookahead(env, planner_wrapper, domain_file, problem_dir):
    total_time = 0
    action_count = 0

    while True:
        obs = env.reset()
        problem_file = problem_state(obs, problem_dir)

        start = time.time()
        plan = planner_wrapper(domain_file, problem_file)
        total_time += time.time() - start

        if plan is None or len(plan)==0:
            return "Success", total_time, action_count

        action = plan[0]
        env.step(action)
        action_count += 1


def run_lazy_lookahead(env, planner_wrapper, domain_file, problem_dir):
    total_time = 0
    action_count = 0
    plan = []

    obs = env.get_state()

    while True:
        if not plan:

            problem_file = problem_state(obs, problem_dir)

            start = time.time()
            plan = planner_wrapper(domain_file, problem_file)
            total_time += time.time() - start

            if plan == []:
                return "Success", total_time, action_count
            if obs.passenger_pos == obs.destination and not obs.passenger_in_taxi:
                return "Success", total_time, action_count


        action = plan.pop(0)
        obs, reward, done, info = env.step(action)
        action_count += 1


