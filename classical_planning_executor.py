import gymnasium as gym
import os
import tempfile
from pyperplan_wrapper import plan
import time
import csv


class SimpleTaxiPlanner:
    LOCATIONS = {'R': (0, 0), 'G': (0, 4), 'Y': (4, 0), 'B': (4, 3)}
    LOC_NAMES = ['R', 'G', 'Y', 'B']

    def __init__(self, domain_file='taxi_domain.pddl'):
        self.domain_file = domain_file
        self.env = None

    def make_problem(self, obs):
        taxi_row, taxi_col, pass_loc, dest_idx = self.env.unwrapped.decode(obs)

        # walls = set()  
        walls = {
            ((0, 0), (0, 1)), ((0, 1), (0, 0)),  # Vertical wall right of R
            ((1, 0), (1, 1)), ((1, 1), (1, 0)),
            ((0, 2), (0, 3)), ((0, 3), (0, 2)),  # Vertical wall right of column 2
            ((1, 2), (1, 3)), ((1, 3), (1, 2)),
            ((3, 0), (3, 1)), ((3, 1), (3, 0)),  # Vertical wall right of column 0
            ((4, 0), (4, 1)), ((4, 1), (4, 0)),
            ((3, 2), (3, 3)), ((3, 3), (3, 2)),  # Vertical wall right of column 2
            ((4, 2), (4, 3)), ((4, 3), (4, 2)),
        }

        pddl = "(define (problem taxi-simple)\n (:domain taxi)\n"
        pddl += "   (:objects taxi1 - taxi passenger1 - passenger\n"

        for i in range(5):
            for j in range(5):
                pddl += f"   loc-{i}-{j} - location\n"
        pddl += "  )\n  (:init\n"

        pddl += f"    (taxi-at taxi1 loc-{taxi_row}-{taxi_col})\n"
        if pass_loc == 4:
            pddl += "    (in-taxi passenger1 taxi1)\n"
        else:
            pr, pc = self.LOCATIONS[self.LOC_NAMES[pass_loc]]
            pddl += f"    (passenger-at passenger1 loc-{pr}-{pc})\n"

        dr, dc = self.LOCATIONS[self.LOC_NAMES[dest_idx]]
        pddl += f"    (destination passenger1 loc-{dr}-{dc})\n"

        for i in range(5):
            for j in range(5):
                if i > 0 and ((i, j), (i - 1, j)) not in walls:
                    pddl += f"    (north loc-{i}-{j} loc-{i - 1}-{j})\n"
                if i < 4 and ((i, j), (i + 1, j)) not in walls:
                    pddl += f"    (south loc-{i}-{j} loc-{i + 1}-{j})\n"
                if j > 0 and ((i, j), (i, j - 1)) not in walls:
                    pddl += f"    (west loc-{i}-{j} loc-{i}-{j - 1})\n"
                if j < 4 and ((i, j), (i, j + 1)) not in walls:
                    pddl += f"    (east loc-{i}-{j} loc-{i}-{j + 1})\n"

        pddl += f"  )\n  (:goal (passenger-at passenger1 loc-{dr}-{dc}))\n)\n"
        return pddl

    def pddl_to_gym_action(self, action_name):
        """
        Actions: 0=south, 1=north, 2=east, 3=west, 4=pickup, 5=dropoff
        """
        action_str = str(action_name).lower()

        if 'north' in action_str:
            return 1
        elif 'south' in action_str:
            return 0
        elif 'east' in action_str:
            return 2
        elif 'west' in action_str:
            return 3
        elif 'pick' in action_str:
            return 4
        elif 'drop' in action_str:
            return 5
        else:
            return 0

    def decode_state(self, obs):
        """Decode observation into human-readable format"""
        taxi_row, taxi_col, pass_loc, dest_idx = self.env.unwrapped.decode(obs)
        pass_loc_str = self.LOC_NAMES[pass_loc] if pass_loc < 4 else "in-taxi"
        dest_str = self.LOC_NAMES[dest_idx]
        return f"Taxi:({taxi_row},{taxi_col}) Pass:{pass_loc_str} Dest:{dest_str}"

    def run_episode_visual(self, seed=None, verbose=True, delay=0.5):
        """Visual version with rendering"""
        self.env = gym.make('Taxi-v3', render_mode='human')
        obs, _ = self.env.reset(seed=seed)

        if verbose:
            print(f"Initial state: {self.decode_state(obs)}")

        done = False
        total_reward = 0
        steps = 0
        plan_count = 0
        current_plan = []
        consecutive_failures = 0
        MAX_CONSECUTIVE_FAILURES = 3
        terminated = False
        reward = 0
        terminated = False  
        reward = 0  

        while not done and steps < 200:
            # Generate new plan if needed
            if not current_plan:
                problem_str = self.make_problem(obs)

                if verbose and steps == 0:
                    print(problem_str)

                with tempfile.NamedTemporaryFile(mode='w', suffix='.pddl', delete=False) as f:
                    f.write(problem_str)
                    problem_file = f.name

                try:
                    plan_result = plan(self.domain_file, problem_file)
                    os.unlink(problem_file)

                    if not plan_result:
                        if verbose:
                            print("ERROR: No plan found!")
                        break

                    current_plan = [a.name if hasattr(a, 'name') else str(a)
                                    for a in plan_result]
                    plan_count += 1

                    if verbose:
                        print(f"Plan {plan_count} ({len(current_plan)} actions): {current_plan}")

                except Exception as e:
                    if verbose:
                        print(f"ERROR: Planning failed - {e}")
                    os.unlink(problem_file)
                    success = False
                    self.env.close()
                    return success, steps, plan_count, total_reward

            
            action_name = current_plan.pop(0)
            gym_action = self.pddl_to_gym_action(action_name)

            if verbose:
                print(f"Step {steps}: {action_name}, gym_action={gym_action}")

            
            old_obs = obs
            old_state = tuple(self.env.unwrapped.decode(obs))

            # Execute action
            obs, reward, terminated, truncated, _ = self.env.step(gym_action)
            new_state = tuple(self.env.unwrapped.decode(obs))

            if verbose:
                print(f"Before: {old_state} | After: {new_state} | Reward: {reward}")

            time.sleep(delay)

            total_reward += reward
            steps += 1
            done = terminated or truncated
            if old_state == new_state and not done:
                consecutive_failures += 1

                # Replan
                if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                    current_plan = []
                    consecutive_failures = 0
            else:
                consecutive_failures = 0
                if verbose and old_state != new_state:
                    print(f"State changed successfully")

        success = terminated and reward > 0
        self.env.close()
            

        return success, steps, plan_count, total_reward

    def run_episode(self, seed=None, verbose=False):
        """Non-visual version for batch testing"""
        self.env = gym.make('Taxi-v3')
        obs, _ = self.env.reset(seed=seed)

        done = False
        total_reward = 0
        steps = 0
        plan_count = 0
        current_plan = []
        consecutive_failures = 0
        MAX_CONSECUTIVE_FAILURES = 3
        terminated = False
        reward = 0

        total_planning_time = 0
        actions_planned = 0
        actions_executed = 0

        while not done and steps < 200:
            if not current_plan:
                if verbose:
                    print(f"[Step {steps}] Planning...")
                problem_str = self.make_problem(obs)

                with tempfile.NamedTemporaryFile(mode='w', suffix='.pddl', delete=False) as f:
                    f.write(problem_str)
                    problem_file = f.name

                try:
                    planning_start = time.time()
                    plan_result = plan(self.domain_file, problem_file)
                    planning_time = time.time() - planning_start
                    total_planning_time += planning_time
                    os.unlink(problem_file)

                    if not plan_result:
                        if verbose:
                            print("No plan found!")
                        break

                    current_plan = [a.name if hasattr(a, 'name') else str(a)
                                    for a in plan_result]
                    
                    
                    if not current_plan:
                        break
                    
                    actions_planned += len(current_plan)
                    plan_count += 1

                except Exception as e:
                    if verbose:
                        print(f"Planning error: {e}")
                    if os.path.exists(problem_file):
                        os.unlink(problem_file)
                    break
            
            # Safety check before popping
            if not current_plan:
                if verbose:
                    print(f"Error: current_plan is empty at step {steps}")
                break

            action_name = current_plan.pop(0)
            gym_action = self.pddl_to_gym_action(action_name)

            old_state = tuple(self.env.unwrapped.decode(obs))
            obs, reward, terminated, truncated, _ = self.env.step(gym_action)
            new_state = tuple(self.env.unwrapped.decode(obs))

            total_reward += reward
            steps += 1
            actions_executed += 1
            done = terminated or truncated

            # Check if state changed
            if old_state == new_state and not done:
                consecutive_failures += 1
                if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                    current_plan = []
                    consecutive_failures = 0
            else:
                consecutive_failures = 0

        success = terminated and reward > 0
        self.env.close()

        fidelity = actions_executed / actions_planned if actions_planned > 0 else 0

        return success, steps, plan_count, total_reward, total_planning_time, fidelity

    def run_episode_lookahead(self, seed=None, verbose=False):
        """Classical Planning with Run-Lookahead (replan every step)"""
        self.env = gym.make('Taxi-v3')
        obs, _ = self.env.reset(seed=seed)

        done = False
        total_reward = 0
        steps = 0
        plan_count = 0
        terminated = False
        reward = 0

        total_planning_time = 0
        actions_planned = 0
        actions_executed = 0

        while not done and steps < 200:
            
            problem_str = self.make_problem(obs)

            with tempfile.NamedTemporaryFile(mode='w', suffix='.pddl', delete=False) as f:
                f.write(problem_str)
                problem_file = f.name

            try:
                planning_start = time.time()
                plan_result = plan(self.domain_file, problem_file)
                planning_time = time.time() - planning_start
                total_planning_time += planning_time
                os.unlink(problem_file)

                if not plan_result:
                    break

                plan_count += 1
                actions_planned += len(plan_result)

                # Execute ONLY first action (Run-Lookahead)
                action = plan_result[0]
                action_name = action.name if hasattr(action, 'name') else str(action)
                gym_action = self.pddl_to_gym_action(action_name)

            except Exception as e:
                if verbose:
                    print(f"Planning error: {e}")
                if os.path.exists(problem_file):
                    os.unlink(problem_file)
                break

            obs, reward, terminated, truncated, _ = self.env.step(gym_action)

            total_reward += reward
            steps += 1
            actions_executed += 1
            done = terminated or truncated

        success = terminated and reward > 0
        self.env.close()

        fidelity = actions_executed / actions_planned if actions_planned > 0 else 0

        return success, steps, plan_count, total_reward, total_planning_time, fidelity


def export_both_to_csv(lazy_results, lookahead_results, filename="classical_results.csv"):
    """Export both classical planning strategies to CSV matching HTN format"""
    with open(filename, "w", newline='') as f:
        writer = csv.writer(f)

        # Header matching your HTN CSV format
        writer.writerow(['Strategy', 'Episode', 'Success', 'Steps', 'Plans', 
                         'Reward', 'Planning_Time', 'Fidelity'])

        # Write Lazy-Lookahead results
        
        for i, r in enumerate(lazy_results):
            success, steps, plans, reward, plan_time, fidelity = r
            writer.writerow(['Classical-Run-Lazy-Lookahead', i + 1, success, steps, plans, reward, plan_time, fidelity])

        # Write Lookahead results
        
        for i, r in enumerate(lookahead_results):
            success, steps, plans, reward, plan_time, fidelity = r
            writer.writerow(['Classical-Run-Lookahead', i + 1, success, steps, plans, reward, plan_time, fidelity])

    print(f"Results exported to {filename}")



if __name__ == "__main__":
    planner = SimpleTaxiPlanner('taxi_domain.pddl')


    success, steps, plans, reward = planner.run_episode_visual(seed=42, verbose=True, delay=0.3)

    print("Classical Planning - RUN-LAZY-LOOKAHEAD Evaluation")
   

    lazy_results = [] 
    for i in range(10):
        success, steps, plans, reward, plan_time, fidelity = planner.run_episode(seed=i, verbose=False)
        lazy_results.append((success, steps, plans, reward, plan_time, fidelity))
        print(f"Episode {i + 1:2d}: | Steps={steps:3d} | Plans={plans:2d} | Reward={reward:6.1f}")


    print("Classical Planning - RUN-LOOKAHEAD Evaluation")


    lookahead_results = [] 
    for i in range(10):
        success, steps, plans, reward, plan_time, fidelity = planner.run_episode_lookahead(seed=i, verbose=False)
        lookahead_results.append((success, steps, plans, reward, plan_time, fidelity))
        print(f"Episode {i + 1:2d}: | Steps={steps:3d} | Plans={plans:2d} | Reward={reward:6.1f}")

    
  
    print("Comparison Summary")

    # Lazy-Lookahead stats
    lazy_success_rate = sum(r[0] for r in lazy_results) / len(lazy_results) * 100
    lazy_avg_steps = sum(r[1] for r in lazy_results) / len(lazy_results)
    lazy_avg_plans = sum(r[2] for r in lazy_results) / len(lazy_results)
    lazy_avg_reward = sum(r[3] for r in lazy_results) / len(lazy_results)
    lazy_avg_plan_time = sum(r[4] for r in lazy_results) / len(lazy_results)

    # Lookahead stats
    lookahead_success_rate = sum(r[0] for r in lookahead_results) / len(lookahead_results) * 100
    lookahead_avg_steps = sum(r[1] for r in lookahead_results) / len(lookahead_results)
    lookahead_avg_plans = sum(r[2] for r in lookahead_results) / len(lookahead_results)
    lookahead_avg_reward = sum(r[3] for r in lookahead_results) / len(lookahead_results)
    lookahead_avg_plan_time = sum(r[4] for r in lookahead_results) / len(lookahead_results)

    

    # Print comparison table
    print(f"{'Metric':<20} {'Run-Lazy-Lookahead':<25} {'Run-Lookahead':<25}")
    print(f"{'Success Rate':<20} {lazy_success_rate:>6.1f}%{'':<18} {lookahead_success_rate:>6.1f}%")
    print(f"{'Avg Steps':<20} {lazy_avg_steps:>6.2f}{'':<19} {lookahead_avg_steps:>6.2f}")
    print(f"{'Avg Plans':<20} {lazy_avg_plans:>6.2f}{'':<19} {lookahead_avg_plans:>6.2f}")
    print(f"{'Avg Reward':<20} {lazy_avg_reward:>6.2f}{'':<19} {lookahead_avg_reward:>6.2f}")
    print(f"{'Avg Planning Time':<20} {lazy_avg_plan_time:>6.3f}s{'':<18} {lookahead_avg_plan_time:>6.3f}s")

    # Export
    export_both_to_csv(lazy_results, lookahead_results, "classical_results.csv")
