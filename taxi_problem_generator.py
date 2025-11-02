def create_problem_file(grid_size, problem_id, taxi_pos, passenger_start, goal_pos):
    locations = [f"loc-{i}-{j}" for i in range(grid_size) for j in range(grid_size)]

    problem = f"""(define (problem taxi-problem-{problem_id})
    (:domain taxi)
    (:objects
        {' '.join(locations)} - location
        taxi1 - taxi
        passenger1 - passenger
    )
    
    (:init
        (taxi-at taxi1 {taxi_pos})
        (passenger-at passenger1 {passenger_start})
        (destination passenger1 {goal_pos})
    """

    for i in range(grid_size):
        for j in range(grid_size):
            if j < grid_size - 1:
                problem += f"   (east loc-{i}-{j} loc-{i}-{j+1})\n"
                problem += f"   (west loc-{i}-{j+1} loc-{i}-{j})\n"

            if i < grid_size - 1:
                problem += f"   (south loc-{i}-{j} loc-{i+1}-{j})\n"
                problem += f"   (north loc-{i+1}-{j} loc-{i}-{j})\n"


    problem += """  )
        (:goal (and
            (passenger-at passenger1 """ + goal_pos + """)
        ))
    )"""

    return problem