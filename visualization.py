import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# Load your results
def load_and_combine_results():
    """Load all CSV results into a single DataFrame"""
    # Load HTN results
    htn_df = pd.read_csv('htn_results.csv')

    # Load Classical results
    classical_df = pd.read_csv('classical_results.csv')

    all_results = pd.concat([htn_df, classical_df], ignore_index=True)

    return all_results


# Calculate summary statistics
def calculate_summary_stats(df):
    """Calculate mean and std for each strategy"""
    summary = df.groupby('Strategy').agg({
        'Success': ['mean', 'std'],
        'Steps': ['mean', 'std'],
        'Plans': ['mean', 'std'],
        'Reward': ['mean', 'std'],
        'Planning_Time': ['mean', 'std'],
        'Fidelity': ['mean', 'std']
    }).round(2)

    return summary


# CHART 1: Success Rate Comparison (Bar Chart)

def plot_success_rate(df):
    """Bar chart comparing success rates"""
    fig, ax = plt.subplots(figsize=(10, 6))

    strategies = df.groupby('Strategy')['Success'].mean() * 100
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']

    bars = ax.bar(range(len(strategies)), strategies.values, color=colors[:len(strategies)])
    ax.set_xticks(range(len(strategies)))
    ax.set_xticklabels(strategies.index, rotation=45, ha='right')
    ax.set_ylabel('Success Rate (%)', fontsize=12)
    ax.set_title('Success Rate Comparison Across Planning Strategies', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3)

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig('success_rate_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()



# CHART 2: Multi-Metric Radar Chart

def plot_radar_chart(df):
    """Radar chart comparing multiple metrics"""
    from math import pi

    # Calculate normalized metrics (0-1 scale)
    summary = df.groupby('Strategy').agg({
        'Success': 'mean',
        'Steps': 'mean',
        'Plans': 'mean',
        'Fidelity': 'mean'
    })

    summary['Success_norm'] = summary['Success']
    summary['Steps_norm'] = 1 - (summary['Steps'] / summary['Steps'].max())
    summary['Plans_norm'] = 1 - (summary['Plans'] / summary['Plans'].max())
    summary['Fidelity_norm'] = summary['Fidelity']

    categories = ['Success\nRate', 'Efficiency\n(fewer steps)', 'Planning\n(fewer calls)', 'Execution\nFidelity']

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='polar')

    angles = [n / float(len(categories)) * 2 * pi for n in range(len(categories))]
    angles += angles[:1]

    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']

    for idx, (strategy, row) in enumerate(summary.iterrows()):
        values = [row['Success_norm'], row['Steps_norm'], row['Plans_norm'], row['Fidelity_norm']]
        values += values[:1]

        ax.plot(angles, values, 'o-', linewidth=2, label=strategy, color=colors[idx])
        ax.fill(angles, values, alpha=0.15, color=colors[idx])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=10)
    ax.set_ylim(0, 1)
    ax.set_title('Multi-Metric Performance Comparison\n(Higher = Better)',
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    ax.grid(True)

    plt.tight_layout()
    plt.savefig('radar_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()



# CHART 3: Planning Overhead vs Success (Scatter Plot)

def plot_overhead_vs_success(df):
    """Scatter plot: Planning overhead vs success rate"""
    fig, ax = plt.subplots(figsize=(10, 6))

    summary = df.groupby('Strategy').agg({
        'Plans': 'mean',
        'Success': 'mean',
        'Steps': 'mean'
    }).reset_index()

    colors = {'HTN-Run-Lookahead': '#2E86AB',
              'HTN-Run-Lazy-Lookahead': '#A23B72',
              'Classical-Run-Lookahead': '#F18F01',
              'Classical-Run-Lazy-Lookahead': '#C73E1D'}

    for _, row in summary.iterrows():
        ax.scatter(row['Plans'], row['Success'] * 100,
                   s=300, alpha=0.6,
                   color=colors.get(row['Strategy'], 'gray'),
                   edgecolors='black', linewidth=1.5)
        ax.annotate(row['Strategy'],
                    (row['Plans'], row['Success'] * 100),
                    xytext=(10, 10), textcoords='offset points',
                    fontsize=9, ha='left')

    ax.set_xlabel('Average Number of Plans per Episode', fontsize=12)
    ax.set_ylabel('Success Rate (%)', fontsize=12)
    ax.set_title('Planning Overhead vs Success Rate', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('overhead_vs_success.png', dpi=300, bbox_inches='tight')
    plt.show()



# CHART 4: Grouped Bar Chart - All Metrics

def plot_grouped_metrics(df):
    """Grouped bar chart for all key metrics"""
    summary = df.groupby('Strategy').agg({
        'Success': 'mean',
        'Steps': 'mean',
        'Plans': 'mean',
        'Fidelity': 'mean'
    })

    # Normalize for visualization (scale 0-100)
    summary['Success_pct'] = summary['Success'] * 100
    summary['Steps_norm'] = (summary['Steps'] / summary['Steps'].max()) * 100
    summary['Plans_norm'] = (summary['Plans'] / summary['Plans'].max()) * 100
    summary['Fidelity_pct'] = summary['Fidelity'] * 100

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Comprehensive Metric Comparison', fontsize=16, fontweight='bold')

    metrics = [
        ('Success_pct', 'Success Rate (%)', axes[0, 0]),
        ('Steps_norm', 'Steps (Normalized)', axes[0, 1]),
        ('Plans_norm', 'Planning Calls (Normalized)', axes[1, 0]),
        ('Fidelity_pct', 'Execution Fidelity (%)', axes[1, 1])
    ]

    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']

    for metric, title, ax in metrics:
        values = summary[metric]
        bars = ax.bar(range(len(values)), values.values, color=colors[:len(values)])
        ax.set_xticks(range(len(values)))
        ax.set_xticklabels(values.index, rotation=45, ha='right', fontsize=9)
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_ylim(0, 110)
        ax.grid(axis='y', alpha=0.3)

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    plt.savefig('all_metrics_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()



# CHART 5: Episode-by-Episode Line Plot

def plot_episode_trends(df):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Performance Trends Across Episodes', fontsize=16, fontweight='bold')

    metrics = [
        ('Success', 'Success (1=Yes, 0=No)', axes[0, 0]),
        ('Steps', 'Steps to Completion', axes[0, 1]),
        ('Plans', 'Number of Plans', axes[1, 0]),
        ('Reward', 'Total Reward', axes[1, 1])
    ]

    for metric, title, ax in metrics:
        for strategy in df['Strategy'].unique():
            strategy_data = df[df['Strategy'] == strategy]
            ax.plot(strategy_data['Episode'], strategy_data[metric],
                    marker='o', label=strategy, linewidth=2, markersize=4)

        ax.set_xlabel('Episode', fontsize=10)
        ax.set_ylabel(title, fontsize=10)
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.legend(fontsize=8, loc='best')
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('episode_trends.png', dpi=300, bbox_inches='tight')
    plt.show()
    



df = load_and_combine_results()

print("Generating Charts comparison")


# Generate all charts
plot_success_rate(df)
plot_radar_chart(df)
plot_overhead_vs_success(df)
plot_grouped_metrics(df)
plot_episode_trends(df)


print("SUMMARY STATISTICS")
print(calculate_summary_stats(df))

print("All charts generated successfully!")