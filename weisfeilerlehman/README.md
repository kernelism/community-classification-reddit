# Weisfeiler-Lehman Kernel Computation and Kernel Matrix Merging

This repository contains two Python scripts, `generate_final_kmatrix.py` and `combination_kmatrix.py`, designed to compute and merge Weisfeiler-Lehman (WL) graph kernel matrices for thousands of graphs. These scripts handle memory constraints by processing the data in manageable 
batches and then recombining the results into a final kernel matrix.

## Overview

The Weisfeiler-Lehman kernel is a widely used graph kernel that computes similarities between graphs based on their structure. Due to the large number of graphs (4032 in this case), directly computing the kernel matrix for all graphs was infeasible due to memory limitations. To address this, the computation was split into smaller subsets, and the results were merged into a complete kernel matrix.

## Scripts

1. combination_kmatrix.py

    - This script computes pairwise Weisfeiler-Lehman kernel matrices for subsets of graphs. It processes every combination of subset since each has unique graphs which need to be compared. 

    - However, for a given pair of subsets *i* & *j* they produce duplicates because WL comparisons return `(A+B, A+B)` similarity matrix where `A` and `B` are the sizes of the subset *i* & *j*.

2. generate_final_kmatrix.py

    - This script merges the individual kernel matrices into a single complete kernel matrix.

    - This script takes into account the duplicates and offsets the indexing appropriately to capture only the similarities from the graphs not accounted for yet, using the sizes of the batches.

    - This allows for fast and efficient graph comparison computations with memory issues when constraints exist.

## Metrics
Loading 4000+ graphs combined with a one-shot run of WL would crash after a **50 min** exec.

<br/>
**Average time to load a pair of batches (around 800 files)**: ~`00:04:20`
<br/>
**Total time taken for all batches**: ~`00:48:00`
<br/>
**Time taken to merge**: `00:01:04`
<br/>
