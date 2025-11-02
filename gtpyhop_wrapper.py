import gtpyhop
from gtpyhop_taxi_domain import *

def plan_with_gtpyhop(state, goal):
    plan = gtpyhop.find_plan(state, goal)
    return plan