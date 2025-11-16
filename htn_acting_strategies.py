"""
HTN Acting Strategies for Taxi-v3
Implements Run-Lookahead and Run-Lazy-Lookahead strategies
Compatible with GTPyhop 1.4.0
"""

import gymnasium as gym
import gtpyhop
import time
from taxi_domain import initialize_domain, decode_gym_obs, action_to_gym


class HTNTaxiExecutor:
    """Executor for HTN planning with different acting strategies"""

    def __init__(self):
        # Initialize the domain (must be called once before planning)
        initialize_domain()
        self.env = None

        # Set global verbosity to 0 (silent) for GTPyhop
        gtpyhop.verbose = 0

    def run_lookahead(self, seed=None, verbose=False, max_steps=200):
        """
        HTN-Run-Lookahead: Aggressive replanning strategy
        """
        self.env = gym.make('Taxi-v3')
        obs, _ = self.env.reset(seed=seed)

        done = False
        total_reward = 0
        steps = 0
        plan_count = 0
        actions_planned = 0
        actions_executed = 0
        total_planning_time = 0

        terminated = False
        truncated = False
        reward = 0

        # Enable verbose for first episode to debug
        debug = (seed == 0)

        if debug:
            print(f"\n{'=' * 60}")
            print(f"HTN-RUN-LOOKAHEAD DEBUG - Seed {seed}")
            print(f"{'=' * 60}")

        while not done and steps < max_steps:
            # PLAN
            state = decode_gym_obs(self.env, obs)

            if debug:
                taxi_row, taxi_col, pass_idx, dest_idx = self.env.unwrapped.decode(obs)
                print(f"\n[Step {steps}] Gym State:")
                print(f"  Raw obs: {obs}")
                print(f"  Decoded: taxi=({taxi_row},{taxi_col}), pass={pass_idx}, dest={dest_idx}")
                print(
                    f"  GTPyhop state: taxi={state.taxi_pos}, pass={state.passenger_loc}, in_taxi={state.passenger_in_taxi}")

            planning_start = time.time()
            plan = gtpyhop.find_plan(state, [('transport',)])
            planning_time = time.time() - planning_start
            total_planning_time += planning_time
            plan_count += 1

            if not plan:
                if debug:
                    print("  ❌ Planning FAILED!")
                break

            actions_planned += len(plan)

            if debug:
                print(f"  📋 Plan ({len(plan)} actions): {plan[:3]}...")

            # ACT
            action = plan[0]
            gym_action = action_to_gym(action)

            if debug:
                print(f"  ▶️  Executing: {action} → Gym action {gym_action}")

            old_obs = obs
            obs, reward, terminated, truncated, _ = self.env.step(gym_action)

            if debug:
                print(f"  Result: obs {old_obs} → {obs}, reward={reward}")
                if obs == old_obs:
                    print(f"  ⚠️  STATE UNCHANGED - ACTION FAILED!")

            total_reward += reward
            steps += 1
            actions_executed += 1
            done = terminated or truncated

        success = terminated and reward > 0
        fidelity = actions_executed / actions_planned if actions_planned > 0 else 0

        if debug:
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"\n{status}: {steps} steps, {plan_count} plans, reward={total_reward}, fidelity={fidelity:.2f}")

        self.env.close()
        return success, steps, plan_count, total_reward, total_planning_time, fidelity

    def run_lazy_lookahead(self, seed=None, verbose=False, max_steps=200):
        """
        HTN-Run-Lazy-Lookahead: Conservative replanning strategy

        Algorithm:
        1. Plan fully from current state
        2. Execute ALL actions from plan until completion or failure
        3. Replan only when plan exhausted or action fails
        """
        self.env = gym.make('Taxi-v3')
        obs, _ = self.env.reset(seed=seed)

        done = False
        total_reward = 0
        steps = 0
        plan_count = 0
        current_plan = []
        actions_planned = 0
        actions_executed = 0
        total_planning_time = 0
        consecutive_failures = 0

        # Initialize these at the start to avoid UnboundLocalError
        terminated = False
        truncated = False
        reward = 0

        if verbose:
            print(f"\n{'='*60}")
            print(f"HTN-RUN-LAZY-LOOKAHEAD - Seed {seed}")
            print(f"{'='*60}")

        while not done and steps < max_steps:
            # PLAN: Only when current plan is exhausted
            if not current_plan:
                state = decode_gym_obs(self.env, obs)

                if verbose:
                    print(f"\n[Step {steps}] ⚙️  REPLANNING from state:")
                    print(f"  Taxi: {state.taxi_pos}, Passenger: {state.passenger_loc}, "
                          f"Dest: {state.destination}, In taxi: {state.passenger_in_taxi}")

                planning_start = time.time()
                plan = gtpyhop.find_plan(state, [('transport',)])
                planning_time = time.time() - planning_start
                total_planning_time += planning_time
                plan_count += 1

                if not plan:
                    if verbose:
                        print("  ❌ Planning FAILED!")
                    break

                current_plan = list(plan)
                actions_planned += len(current_plan)

                if verbose:
                    print(f"  📋 New plan ({len(current_plan)} actions): {current_plan}")
                    print(f"  ⏱️  Planning time: {planning_time:.4f}s")

            # ACT: Execute next action from current plan
            action = current_plan.pop(0)
            gym_action = action_to_gym(action)

            if verbose:
                print(f"  ▶️  [{steps}] {action}")

            old_obs = obs
            obs, reward, terminated, truncated, _ = self.env.step(gym_action)

            total_reward += reward
            steps += 1
            actions_executed += 1
            done = terminated or truncated

            # MONITOR: Detect action failures (state unchanged)
            if obs == old_obs and not done:
                consecutive_failures += 1
                if verbose:
                    print(f"  ⚠️  Action had no effect! (failure #{consecutive_failures})")

                # Trigger replanning after failure
                if consecutive_failures >= 2:
                    if verbose:
                        print("  🔄 Multiple failures detected - clearing plan")
                    current_plan = []
                    consecutive_failures = 0
            else:
                consecutive_failures = 0

        success = terminated and reward > 0
        fidelity = actions_executed / actions_planned if actions_planned > 0 else 0

        if verbose:
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"\n{status}: {steps} steps, {plan_count} plans, reward={total_reward}")

        self.env.close()
        return success, steps, plan_count, total_reward, total_planning_time, fidelity
