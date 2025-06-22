# config.py

# --- Simulation Environment ---
NUM_ACCOUNTS = 50000
NUM_EPOCHS = 100
EPOCH_DURATION_S = 5 * 60  # 5 minutes in seconds

# --- Workload Generation ---
# Baseline traffic
TX_PER_EPOCH_BASELINE = 80000
POWER_LAW_ALPHA = 2.5  # Controls the skew of transactions

# Event-Driven Spike
SPIKE_EPOCH = 50
SPIKE_TX_COUNT = 400000  # A massive spike
NFT_CLUSTER_SIZE = 10
# Accounts from 1000 to 1009 are designated as the NFT dApp contracts
NFT_CLUSTER_ACCOUNTS = set(range(1000, 1000 + NFT_CLUSTER_SIZE))

# --- Evaluation Metrics ---
# Latency assumptions (in seconds)
LATENCY_INTRA_SHARD = 2.0
LATENCY_CROSS_SHARD = 10.0 # CSTs are 5x more expensive

# --- ProShard Protocol Parameters ---
# Weights for the Predictive Affinity Graph (PAG)
# w(e_ij) = alpha * H + beta * P + gamma * S
PAG_WEIGHTS = {
    'historical': 0.2,  # alpha
    'predictive': 0.5,  # beta
    'semantic': 0.3,    # gamma
}

# EMA (Exponential Moving Average) parameter for prediction
EMA_ALPHA = 0.3

# Threshold for an account to be considered "high-activity" for prediction
PREDICTION_ACTIVITY_THRESHOLD = 50