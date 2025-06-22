# simulator.py

import numpy as np
import pandas as pd
from collections import defaultdict
import config

class Simulator:
    def __init__(self, protocol):
        self.protocol = protocol
        self.num_accounts = protocol.num_accounts
        self.num_shards = protocol.num_shards

        self.partition = {i: i % self.num_shards for i in range(self.num_accounts)}
        self.workload_history = {}
        self.results = []

    def _generate_workload(self, epoch):
        """Generates transactions for the current epoch."""
        # 1. Baseline traffic (Power-law)
        # Generate pairs of interacting accounts based on a Zipfian distribution
        s = np.random.zipf(config.POWER_LAW_ALPHA, config.TX_PER_EPOCH_BASELINE * 2)
        accounts = s % self.num_accounts
        txs = list(zip(accounts[::2], accounts[1::2]))
        
        # 2. Event-driven spike
        if epoch == config.SPIKE_EPOCH:
            spike_src = np.random.randint(0, self.num_accounts, config.SPIKE_TX_COUNT)
            spike_dst = np.random.choice(list(config.NFT_CLUSTER_ACCOUNTS), config.SPIKE_TX_COUNT)
            txs.extend(list(zip(spike_src, spike_dst)))
            
        return txs

    def _process_transactions(self, transactions, current_partition):
        """Simulates transaction processing and gathers metrics for the epoch."""
        num_cst = 0
        total_latency = 0
        shard_load = defaultdict(int)

        for src, dst in transactions:
            src_shard = current_partition.get(src)
            dst_shard = current_partition.get(dst)

            shard_load[src_shard] += 1
            shard_load[dst_shard] += 1

            if src_shard != dst_shard:
                num_cst += 1
                total_latency += config.LATENCY_CROSS_SHARD
            else:
                total_latency += config.LATENCY_INTRA_SHARD
        
        num_txs = len(transactions)
        avg_latency = total_latency / num_txs if num_txs > 0 else 0
        cst_ratio = (num_cst / num_txs) * 100 if num_txs > 0 else 0
        throughput = num_txs / config.EPOCH_DURATION_S

        # Workload imbalance
        loads = [v for v in shard_load.values() if v > 0]
        imbalance = max(loads) / min(loads) if len(loads) > 1 else 1.0
        
        return {
            'throughput': throughput,
            'avg_latency': avg_latency,
            'cst_ratio': cst_ratio,
            'imbalance': imbalance,
            'num_cst': num_cst
        }

    def run(self):
        """Runs the full simulation for NUM_EPOCHS."""
        print(f"\n--- Running Simulation for: {self.protocol.name} ---")
        for epoch in range(config.NUM_EPOCHS):
            print(f"\rEpoch {epoch+1}/{config.NUM_EPOCHS}", end="")

            # 1. Generate this epoch's workload
            transactions = self._generate_workload(epoch)
            self.workload_history[epoch] = [(t[0], t[1]) for t in transactions]

            # 2. Protocol decides on new partition
            old_partition = self.partition.copy()
            new_partition = self.protocol.reconfigure(old_partition, self.workload_history, epoch)
            self.partition = new_partition

            # 3. Calculate reconfiguration cost
            moved_accounts = sum(1 for acc, shd in old_partition.items() if new_partition.get(acc) != shd)
            reconfig_cost = (moved_accounts / self.num_accounts) * 100

            # 4. Process transactions with the new partition and get metrics
            epoch_metrics = self._process_transactions(transactions, self.partition)
            epoch_metrics['epoch'] = epoch
            epoch_metrics['reconfig_cost'] = reconfig_cost
            
            self.results.append(epoch_metrics)
        print("\nSimulation complete.")
        return pd.DataFrame(self.results)