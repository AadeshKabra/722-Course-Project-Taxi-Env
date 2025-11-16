"""
Main evaluation script for HTN acting strategies on Taxi-v3
Compares Run-Lookahead vs Run-Lazy-Lookahead
"""

import csv
from htn_acting_strategies import HTNTaxiExecutor


def evaluate_strategy(executor, strategy_name, strategy_func, num_episodes=10, verbose_first=True):

    print(f"\n{'=' * 70}")
    print(f"{strategy_name.upper()} EVALUATION")
    print(f"{'=' * 70}")

    results = []

    for i in range(num_episodes):
        verbose = (i == 0 and verbose_first)
        success, steps, plans, reward, plan_time, fidelity = \
            strategy_func(seed=i, verbose=verbose)

        results.append((success, steps, plans, reward, plan_time, fidelity))

        if not verbose:  # Only print summary if not verbose
            status = "✓" if success else "✗"
            print(f"Episode {i + 1:2d}: {status} | Steps={steps:3d} | Plans={plans:3d} | "
                  f"Reward={reward:4.0f} | Time={plan_time:6.3f}s | Fidelity={fidelity:.2f}")

    return results


def print_comparison(lookahead_results, lazy_results):
    """Print detailed comparison of both strategies"""
    print(f"\n{'=' * 70}")
    print("COMPARISON SUMMARY")
    print(f"{'=' * 70}\n")

    metrics = [
        ("Success Rate", lambda r: sum(x[0] for x in r) / len(r) * 100, "%"),
        ("Avg Steps", lambda r: sum(x[1] for x in r) / len(r), ""),
        ("Avg Plans", lambda r: sum(x[2] for x in r) / len(r), ""),
        ("Avg Reward", lambda r: sum(x[3] for x in r) / len(r), ""),
        ("Avg Planning Time", lambda r: sum(x[4] for x in r) / len(r), "s"),
        ("Avg Fidelity", lambda r: sum(x[5] for x in r) / len(r), ""),
    ]

    print(f"{'Metric':<25} {'Run-Lookahead':<20} {'Run-Lazy-Lookahead':<20}")
    print("-" * 70)

    for name, func, unit in metrics:
        la_val = func(lookahead_results)
        lazy_val = func(lazy_results)

        if unit == "%":
            print(f"{name:<25} {la_val:>6.1f}{unit:<14} {lazy_val:>6.1f}{unit:<14}")
        elif unit == "s":
            print(f"{name:<25} {la_val:>6.3f}{unit:<14} {lazy_val:>6.3f}{unit:<14}")
        else:
            print(f"{name:<25} {la_val:>6.2f}{unit:<14} {lazy_val:>6.2f}{unit:<14}")


def export_results(lookahead_results, lazy_results, filename="htn_results.csv"):
    """Export results to CSV for further analysis"""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Strategy', 'Episode', 'Success', 'Steps', 'Plans',
                         'Reward', 'Planning_Time', 'Fidelity'])

        for i, r in enumerate(lookahead_results):
            writer.writerow(['Run-Lookahead', i + 1] + list(r))

        for i, r in enumerate(lazy_results):
            writer.writerow(['Run-Lazy-Lookahead', i + 1] + list(r))

    print(f"\n✅ Results exported to {filename}")


if __name__ == '__main__':
    executor = HTNTaxiExecutor()

    # Evaluate both strategies
    lookahead_results = evaluate_strategy(
        executor,
        "HTN-Run-Lookahead",
        executor.run_lookahead,
        num_episodes=10,
        verbose_first=False
    )

    lazy_results = evaluate_strategy(
        executor,
        "HTN-Run-Lazy-Lookahead",
        executor.run_lazy_lookahead,
        num_episodes=10,
        verbose_first=False
    )

    # Print comparison
    print_comparison(lookahead_results, lazy_results)

    # Export to CSV
    export_results(lookahead_results, lazy_results)
