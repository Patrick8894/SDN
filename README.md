# Performance Evaluation of Software-Defined Networking using Mininet and Ryu Controller

**Authors**: Bo-Hao Wu (bohaowu2@illinois.edu), Chun-Chieh Chang (cc132@illinois.edu)

## Abstract

Software-Defined Networking (SDN) enables centralized control and programmability over network operations. This report compares simple and advanced SDN switches against traditional OSPF networks. Evaluations focus on performance metrics like throughput, latency, and scalability.

## Introduction

SDN facilitates programmatic network control using OpenFlow, while OSPF relies on distributed protocols. This study compares SDN and OSPF networks under different traffic patterns and topology sizes.

## Background and Related Work

- **Mininet:** A network emulator for testing virtual networks.
- **Ryu:** A Python-based SDN framework.
- **OpenFlow:** Protocol for SDN controllers to manage network switches.
- **OSPF:** Traditional routing protocol for dynamic path selection.

## Problem Statement

Key metrics assessed include:

1. Topology impact on performance
2. Latency differences between SDN and OSPF
3. Scalability and bandwidth comparisons

## Methods

### Network Setup

- **Mininet:** Linear and tree topologies with variable sizes.
- **Ryu Controllers:** 
  - Simple SDN Switch
  - Advanced SDN Switch (Dijkstra algorithm)

### Traffic Measurement

- **Iperf:** For throughput and bandwidth.
- **Ping:** For latency.
- **Metrics:** RTT and bandwidth (Gbps).

## Results

### Average RTT
The average RTT for the furthest hosts shows that SDN switches have higher latency in large networks compared to OSPF.

<p align="center">
  <img src="https://github.com/Patrick8894/SDN/assets/38349902/d9e9deef-f37e-4e0f-981c-9981e0c70368" width="50%" alt="Avg_rtt">
</p>

### Maximum RTT
Maximum RTT follows a similar pattern. The initial learning process of SDN switches significantly affects the first packet's latency.

<p align="center">
  <img src="https://github.com/Patrick8894/SDN/assets/38349902/28501618-48a6-439a-8282-101c68d966b8" width="50%" alt="Max_rtt">
</p>

### Bandwidth
Bandwidth remains consistent across network topologies, except for cases with long path lengths.

<p align="center">
  <img src="https://github.com/Patrick8894/SDN/assets/38349902/408d5c05-1339-4221-b21e-417e67dcd91f" width="50%" alt="Bandwidth">
</p>


## Discussion and Comparison

- **Latency:** OSPF has lower latency due to decentralized routing.
- **Throughput and Bandwidth:** Simple SDN matches OSPF in small networks, but advanced switches improve performance using pre-computed paths.

## Conclusion and Future Work

SDN's centralized control faces challenges in scalability and performance. Future work involves optimized controllers, routing algorithms, and SDN switches with STP to handle loops.
