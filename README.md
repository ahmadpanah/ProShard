# ProShard: A Proactive Sharding Protocol Simulator

This repository contains a Python-based simulation of the **ProShard** protocol, as described in the research paper *"ProShard: Proactive Sharding for Scalable Blockchains via Semantic and Predictive On-Chain Analysis"*.

The simulation framework evaluates ProShard's performance against several other sharding protocols (Static, CLPA, and an advanced reactive model) across four distinct scenarios, validating its effectiveness in mitigating congestion and improving scalability.

## Features

- **Protocol Simulation**: Implements five distinct sharding protocols:
  - **ProShard (Proactive)**: The featured protocol, using semantic, predictive, and historical data.
  - **DBSRP-ML (Advanced Reactive)**: Simulates a state-of-the-art reactive protocol using graph-based partitioning on historical data.
  - **CLPA (Reactive)**: A simpler reactive protocol using the Community Label Propagation Algorithm.
  - **Static (Address-based)**: A baseline protocol similar to Monoxide, where shards are assigned based on account address.
- **Realistic Workload Generation**:
  - **Baseline Traffic**: A steady stream of transactions following a power-law distribution, typical of public blockchains.
  - **Event-Driven Spikes**: Simulates high-volume, localized events like NFT mints to test protocol responsiveness.
- **Comprehensive Evaluation**: Runs the four key scenarios described in the paper:
  1. **Steady-State Performance**: Measures baseline efficiency.
  2. **Sudden Workload Spike**: Tests the protocol's reaction to a sudden congestion event.
  3. **Scalability**: Evaluates performance as the number of shards increases.
  4. **Reconfiguration Cost**: Measures the stability of the sharding configuration over time.
- **Data Export**: Saves the final results of each scenario into `.csv` files for easy analysis and plotting.

## Repository Structure
```
/
├── config.py                # All tunable parameters for the simulation
├── protocols.py             # Implementation of the sharding protocols
├── simulator.py             # The main simulation engine
├── main.py                  # The entry point to run all scenarios
├── README.md                # This file
└── simulation_results/      # Directory created after running the simulation
    ├── scenario_1_steady_state.csv
    ├── scenario_2_workload_spike.csv
    ├── scenario_3_scalability.csv
    └── scenario_4_reconfiguration_cost.csv
```

## Prerequisites

- Python 3.8 or newer
- pip (Python's package installer)

## How to Run

### 1. Clone the Repository
git clone https://github.com/ahmadpanah/proshard.git
cd proshard-simulator

### 2. Install Dependencies
The simulation requires the pandas and networkx libraries. Install them using pip:
```
pip install pandas networkx
```

### 3. Run the Simulation
Execute the main.py script from your terminal. It will automatically run all four scenarios. The simulation will take a few minutes to complete, depending on your system's performance.
python main.py

## Expected Output

When you run the script, you will see:
- Progress updates printed to the console as each scenario is simulated
- Final summary tables for all four scenarios displayed in the terminal
- A new directory named `simulation_results` will be created in the project root

This directory will contain four `.csv` files with the summary data, which can be opened in any spreadsheet software for further analysis or plotting:
- scenario_1_steady_state.csv
- scenario_2_workload_spike.csv
- scenario_3_scalability.csv
- scenario_4_reconfiguration_cost.csv

<div align="center">
  ![A high-level overview of the ProShard simulation pipeline. After setup and dependency installation, the simulator runs multiple sharding protocols across four distinct blockchain workload scenarios.](https://github.com/ahmadpanah/ProShard/blob/211fcebe97322a24072baddb6c05b168c3a32cde/simulation_run.png)
</div>

This implementation is based on the research paper: ProShard: Proactive Sharding for Scalable Blockchains via Semantic and Predictive On-Chain Analysis by Seyed Hossein Ahmadpanah and Meghdad Mirabi.