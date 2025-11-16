# from pyperplan import planner as pyperplan
#
# def plan(domain_file, problem_file):
#     plan = pyperplan.search_plan(domain_file, problem_file, search="astar", heuristic="hff")
#
#     return plan


from pyperplan.planner import _parse, _ground, SEARCHES, HEURISTICS


def plan(domain_file, problem_file):
    problem = _parse(domain_file, problem_file)

    task = _ground(problem)

    search_func = SEARCHES['astar']
    heuristic_class = HEURISTICS['hff']

    heuristic = heuristic_class(task)

    solution = search_func(task, heuristic)

    return solution
