# main.py

import pandas as pd
import config
from simulator import Simulator
from protocols import StaticProtocol, CLPAProtocol, DBSRPMLProtocol, ProShardProtocol

def run_scenario_1(protocols):
    """Steady-State Baseline Performance (S=16)"""
    print("\n\n" + "="*20 + " SCENARIO 1: Steady-State Baseline " + "="*20)
    results = []
    # Temporarily disable the spike for this scenario
    original_spike_epoch = config.SPIKE_EPOCH
    config.SPIKE_EPOCH = -1 

    for proto_class in protocols:
        sim = Simulator(proto_class(num_shards=16, num_accounts=config.NUM_ACCOUNTS))
        df = sim.run()
        results.append({
            'Protocol': sim.protocol.name,
            'Avg. Throughput (TPS)': df['throughput'].mean(),
            'Avg. Latency (s)': df['avg_latency'].mean(),
            'CST Ratio (%)': df['cst_ratio'].mean()
        })
    
    config.SPIKE_EPOCH = original_spike_epoch # Restore config
    df_results = pd.DataFrame(results)
    print("\n--- Results for Scenario 1 ---")
    print(df_results.to_string(index=False))

def run_scenario_2(protocols):
    """Reaction to a Sudden Workload Spike (Epoch 50)"""
    print("\n\n" + "="*20 + " SCENARIO 2: Sudden Workload Spike " + "="*20)
    results = []
    
    for proto_class in protocols:
        sim = Simulator(proto_class(num_shards=16, num_accounts=config.NUM_ACCOUNTS))
        df = sim.run()
        spike_data = df[df['epoch'] == config.SPIKE_EPOCH].iloc[0]
        results.append({
            'Protocol': sim.protocol.name,
            'Peak Latency (s)': spike_data['avg_latency'],
            'Peak CST Ratio (%)': spike_data['cst_ratio'],
            'Peak Imbalance': f"{spike_data['imbalance']:.1f}x"
        })
    
    df_results = pd.DataFrame(results)
    print("\n--- Results for Scenario 2 ---")
    print(df_results.to_string(index=False))
    
def run_scenario_3(protocols):
    """Scalability with Increasing Number of Shards"""
    print("\n\n" + "="*20 + " SCENARIO 3: Scalability " + "="*20)
    shard_counts = [4, 16, 32, 64]
    results_dict = defaultdict(list)

    for proto_class in protocols:
        for s in shard_counts:
            print(f"\nTesting {proto_class.__name__} with S={s}...")
            sim = Simulator(proto_class(num_shards=s, num_accounts=config.NUM_ACCOUNTS))
            df = sim.run()
            # Use max throughput as the metric
            results_dict[sim.protocol.name].append(df['throughput'].max())

    df_results = pd.DataFrame(results_dict, index=[f"S={s}" for s in shard_counts]).T
    df_results.index.name = "Protocol"
    print("\n--- Results for Scenario 3 (Max System Throughput - TPS) ---")
    print(df_results)

def run_scenario_4(protocols):
    """Reconfiguration Cost and Stability"""
    print("\n\n" + "="*20 + " SCENARIO 4: Reconfiguration Cost " + "="*20)
    results = []
    
    for proto_class in protocols:
        sim = Simulator(proto_class(num_shards=16, num_accounts=config.NUM_ACCOUNTS))
        df = sim.run()
        avg_reconfig = df[df['epoch'] > 0]['reconfig_cost'].mean() # Exclude initial setup
        results.append({
            'Protocol': sim.protocol.name,
            'Avg. % of Accounts Migrated': f"{avg_reconfig:.1f}%"
        })
    
    df_results = pd.DataFrame(results)
    print("\n--- Results for Scenario 4 ---")
    print(df_results.to_string(index=False))

if __name__ == "__main__":
    # The list of protocols to be evaluated
    protocol_classes = [
        StaticProtocol,
        CLPAProtocol,
        DBSRPMLProtocol,
        ProShardProtocol
    ]
    
    # We are replacing Metis-Graph with CLPA as they serve a similar purpose
    # and CLPA is readily available in networkx.
    print("NOTE: Metis-Graph is represented by CLPA in this simulation.")
    
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    run_scenario_1(protocol_classes)
    run_scenario_2(protocol_classes)
    run_scenario_3(protocol_classes)
    run_scenario_4(protocol_classes)