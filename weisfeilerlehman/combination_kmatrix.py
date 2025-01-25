import glob
import numpy as np
import os
import logging
import pickle
from datetime import datetime
import concurrent.futures as mp
from grakel.kernels import WeisfeilerLehman, VertexHistogram
from itertools import combinations
from generate_final_kmatrix import process_graph

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

def graph_processor(all_graphs):
    start_time = datetime.now()
    logging.info(f"Starting at {start_time}")   

    logging.info(f"Found {len(all_graphs)} files")

    with mp.ProcessPoolExecutor() as executor:
        results = list(executor.map(process_graph, all_graphs))

    graphs = [graph for graph in results if graph is not None]
    end_time = datetime.now()   

    logging.info(f"Finished at {end_time}")
    logging.info(f"Total time taken: {end_time - start_time}")

    return graphs

def main(subset_index_i, subset_index_j, n_subsets=10):
    # List of all graph files
    list_of_files = glob.glob('v2/graphs/*/*.graphml')
    logger.info(f"Found {len(list_of_files)} files")

    # Divide files into subsets
    file_subsets = np.array_split(list_of_files, n_subsets)
    graph_files = file_subsets[subset_index_i]
    graph_files_v2 = file_subsets[subset_index_j]
    all_graphs = np.concatenate((graph_files, graph_files_v2))
    logger.info(f"Processing subset {subset_index_i} & {subset_index_j} with {len(all_graphs)} files")

    # Process the graphs in this subset
    graphs = graph_processor(all_graphs)
    
    kernel_file = f'kernel_matrix_{subset_index_i}_{subset_index_j}.pkl'

    # Compute the kernel matrix
    kernel_matrix = compute_isomorphism_subset(graphs)
    save_kernel_matrix(kernel_matrix, kernel_file)

if __name__ == '__main__':
    for i, j in combinations(range(10), 2):
        if os.path.exists(f'kernel_matrix_{i}_{j}.pkl'):
            continue
        main(i, j)
    