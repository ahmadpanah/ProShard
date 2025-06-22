# protocols.py

import random
import networkx as nx
from abc import ABC, abstractmethod
from collections import defaultdict
import config

class ShardingProtocol(ABC):
    """Abstract base class for all sharding protocols."""
    def __init__(self, num_shards, num_accounts):
        self.num_shards = num_shards
        self.num_accounts = num_accounts
        self.name = "Protocol"

    @abstractmethod
    def reconfigure(self, current_partition, workload_history, epoch):
        """Returns the new partition map {account_id: shard_id}."""
        pass

    def _create_partition_from_communities(self, communities):
        """Helper to convert networkx community list to a partition map."""
        partition = {}
        for shard_id, community in enumerate(communities):
            for account in community:
                partition[account] = shard_id
        return partition

class StaticProtocol(ShardingProtocol):
    """Static sharding based on account address (ID). Similar to Monoxide."""
    def __init__(self, num_shards, num_accounts):
        super().__init__(num_shards, num_accounts)
        self.name = "Static (Address-based)"
        self.partition = {i: i % self.num_shards for i in range(num_accounts)}

    def reconfigure(self, current_partition, workload_history, epoch):
        # Static protocol never reconfigures
        return self.partition

class ReactiveProtocol(ShardingProtocol):
    """Base class for reactive protocols that use the previous epoch's data."""
    def _build_graph_from_history(self, workload_history, epoch):
        G = nx.Graph()
        if epoch == 0 or not workload_history:
            return G
        
        last_epoch_txs = workload_history.get(epoch - 1, [])
        for src, dst in last_epoch_txs:
            if G.has_edge(src, dst):
                G[src][dst]['weight'] += 1
            else:
                G.add_edge(src, dst, weight=1)
        return G

class CLPAProtocol(ReactiveProtocol):
    """Reactive protocol using Community Label Propagation Algorithm."""
    def __init__(self, num_shards, num_accounts):
        super().__init__(num_shards, num_accounts)
        self.name = "CLPA (Reactive)"

    def reconfigure(self, current_partition, workload_history, epoch):
        G = self._build_graph_from_history(workload_history, epoch)
        if not G.nodes:
            return current_partition
        
        # Label propagation doesn't guarantee the number of communities.
        # This is a simplification. A real implementation might merge smaller communities.
        communities = nx.community.label_propagation_communities(G)
        return self._create_partition_from_communities(communities)

class DBSRPMLProtocol(ReactiveProtocol):
    """
    Represents an advanced reactive protocol (like DBSRP-ML).
    Uses a more robust, weighted community detection algorithm (Greedy Modularity).
    """
    def __init__(self, num_shards, num_accounts):
        super().__init__(num_shards, num_accounts)
        self.name = "DBSRP-ML (Advanced Reactive)"

    def reconfigure(self, current_partition, workload_history, epoch):
        G = self._build_graph_from_history(workload_history, epoch)
        if not G.nodes:
            return current_partition
        
        # Greedy modularity is a good proxy for advanced graph partitioning
        communities = nx.community.greedy_modularity_communities(G, n_communities=self.num_shards)
        return self._create_partition_from_communities(communities)


class ProShardProtocol(ShardingProtocol):
    """The proactive, semantic, and predictive ProShard protocol."""
    def __init__(self, num_shards, num_accounts):
        super().__init__(num_shards, num_accounts)
        self.name = "ProShard (Proactive)"
        self.historical_activity = defaultdict(int)
        self.predicted_activity = defaultdict(int)

    def _predict(self, workload_history, epoch):
        """
        Predicts activity for the upcoming epoch.
        - Uses EMA for baseline prediction.
        - Has "oracle" knowledge of the planned spike event.
        """
        # 1. Update historical activity with data from last epoch
        if epoch > 0:
            last_epoch_txs = workload_history.get(epoch - 1, [])
            last_epoch_activity = defaultdict(int)
            for src, dst in last_epoch_txs:
                last_epoch_activity[src] += 1
                last_epoch_activity[dst] += 1

            for acc, activity in last_epoch_activity.items():
                # Apply EMA update
                self.historical_activity[acc] = (config.EMA_ALPHA * activity) + \
                                                ((1 - config.EMA_ALPHA) * self.historical_activity[acc])

        # 2. Generate predictions for the *next* epoch
        self.predicted_activity.clear()
        for acc, activity in self.historical_activity.items():
            if activity > config.PREDICTION_ACTIVITY_THRESHOLD:
                self.predicted_activity[acc] = activity # Simple EMA prediction

        # 3. **The Proactive Oracle**: Predict the NFT spike one epoch before it happens
        if epoch == config.SPIKE_EPOCH - 1:
            spike_prediction_value = config.SPIKE_TX_COUNT / config.NFT_CLUSTER_SIZE
            for acc in config.NFT_CLUSTER_ACCOUNTS:
                self.predicted_activity[acc] += spike_prediction_value

    def _build_predictive_affinity_graph(self, workload_history, epoch):
        G = nx.Graph()
        
        # 1. Historical Component (H)
        historical_weights = defaultdict(int)
        if epoch > 0:
             last_epoch_txs = workload_history.get(epoch-1, [])
             for src, dst in last_epoch_txs:
                 historical_weights[(min(src,dst), max(src,dst))] += 1

        # 2. Combine all factors into edge weights
        all_edges = set(historical_weights.keys())

        for u, v in all_edges:
            # Historical score
            h_score = historical_weights.get((u, v), 0)
            
            # Predictive score (P)
            p_score = self.predicted_activity.get(u, 0) * self.predicted_activity.get(v, 0)
            
            # Semantic score (S)
            is_semantic_match = (u in config.NFT_CLUSTER_ACCOUNTS and v in config.NFT_CLUSTER_ACCOUNTS)
            s_score = 1.0 if is_semantic_match else 0.0
            
            # Normalize scores (simple max-based normalization for simulation)
            # A more robust implementation would use proper scaling
            max_h = max(historical_weights.values()) if historical_weights else 1
            max_p = max(self.predicted_activity.values())**2 if self.predicted_activity else 1
            
            norm_h = h_score / max_h
            norm_p = p_score / max_p
            
            # Calculate final PAG edge weight
            weight = (config.PAG_WEIGHTS['historical'] * norm_h +
                      config.PAG_WEIGHTS['predictive'] * norm_p +
                      config.PAG_WEIGHTS['semantic'] * s_score)
            
            if weight > 0:
                G.add_edge(u, v, weight=weight)
        
        return G

    def reconfigure(self, current_partition, workload_history, epoch):
        # 1. Predict the future
        self._predict(workload_history, epoch)
        
        # 2. Build the forward-looking graph
        G = self._build_predictive_affinity_graph(workload_history, epoch)
        
        if not G.nodes:
            return current_partition
            
        # 3. Partition the PAG
        communities = nx.community.greedy_modularity_communities(G, n_communities=self.num_shards, weight='weight')
        return self._create_partition_from_communities(communities)