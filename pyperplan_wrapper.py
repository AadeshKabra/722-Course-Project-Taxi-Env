from pyperplan import planner as pyperplan

def plan(domain_file, problem_file):
    plan = pyperplan.search_plan(domain_file, problem_file, search="astar", heuristic_class='hff')

    return plan