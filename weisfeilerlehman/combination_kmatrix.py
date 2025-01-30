import glob
import numpy as np
import networkx as nx
import os
import logging
import pickle
from datetime import datetime
import concurrent.futures as mp
from grakel.kernels import WeisfeilerLehman, VertexHistogram
from itertools import combinations
import time

KERNEL_MATRICES_BP = "./kernel_matrices_v2/"
GRAPHS_BP = "/Users/arjuns/Downloads/notebooks_v2/v2/graphs"
list_of_files = glob.glob(f'{GRAPHS_BP}/*/*.graphml')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_edge_dictionary(G):
    edge_dict = {}
    for node in G.nodes():
        edge_dict[node] = {}
        
        for neighbor in G.neighbors(node):
            edge_dict[node][neighbor] = 0
            
    return edge_dict

def create_node_labels(G):
    node_labels = {node: node for node in G.nodes()}
    return node_labels

def convert_to_grakel_format_with_edge_dict(G):
    edge_dict = create_edge_dictionary(G)
    node_labels = create_node_labels(G)
    return edge_dict, node_labels

def compute_isomorphism_subset(graph_subset):
    logger.info('Starting computation for a subset')
    kernel = WeisfeilerLehman(normalize=True, base_graph_kernel=VertexHistogram)
    kernel_matrix = kernel.fit_transform(graph_subset)
    logger.info('Finished computation for a subset')
    return kernel_matrix

def save_kernel_matrix(kernel_matrix, filename):
    with open(filename, 'wb') as f:
        pickle.dump(kernel_matrix, f)
    logger.info(f'Saved kernel matrix to {filename}')

def process_graph_parallel(graph_file):
    print(f"Processing {graph_file}...")
    try:
        nx_graph = nx.read_graphml(graph_file)
        if nx_graph.number_of_nodes() == 0 or nx_graph.number_of_edges() == 0:
            return None
        graph = convert_to_grakel_format_with_edge_dict(nx_graph)
        return graph
    except Exception as e:
        print(f"Error processing {graph_file}: {e}")
        return None

def graph_processor(all_graphs):
    start_time = datetime.now()
    logging.info(f"Starting at {start_time}")   

    logging.info(f"Found {len(all_graphs)} graphs")

    with mp.ProcessPoolExecutor() as executor:
        results = list(executor.map(process_graph_parallel, all_graphs))

    graphs = [graph for graph in results if graph is not None]
    end_time = datetime.now()   

    logging.info(f"Finished at {end_time}")
    logging.info(f"Total time taken: {end_time - start_time}")

    return graphs

def main(primary_subset, subset_index_i, subset_index_j, n_subsets=10):
    secondary_subset = load_subset(subset_index_j, n_subsets=n_subsets)
    all_graphs = np.concatenate((primary_subset, secondary_subset))
    logger.info(f"Processing subset {subset_index_i} & {subset_index_j} with {len(all_graphs)} files")
    
    kernel_file = f'kernel_matrix_{subset_index_i}_{subset_index_j}.pkl'

    # Compute the kernel matrix
    kernel_matrix = compute_isomorphism_subset(all_graphs)
    save_kernel_matrix(kernel_matrix, kernel_file)

def load_subset(subset_index, n_subsets=10):
    file_subsets = np.array_split(list_of_files, n_subsets)
    graph_files = file_subsets[subset_index]
    all_graphs = graph_processor(graph_files)
    return all_graphs

if __name__ == '__main__':
    times = []
    primary_subset = None
    primary_subset_idx = None
    for i, j in combinations(range(10), 2):
        if os.path.exists(f'{KERNEL_MATRICES_BP}/kernel_matrix_{i}_{j}.pkl'):
            continue
        start_time = time.time()
        if primary_subset is None or primary_subset_idx != i:
            primary_subset = load_subset(i)
            primary_subset_idx = i
        main(primary_subset, i, j)
        end_time = time.time()
        times.append(end_time - start_time)

    logging.info(f"Total time taken: {sum(times)}")
    logging.info(f"Average time taken: {sum(times)/len(times)}")
    