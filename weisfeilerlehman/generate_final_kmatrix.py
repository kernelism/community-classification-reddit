import glob
import os
import numpy as np
import networkx as nx
import pickle
import logging
from itertools import combinations

def load_kernel_matrix(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)
    
def merge_kernel_matrices(n_subsets=10):
    sizes = [405, 405, 405, 405, 393, 399, 405, 405, 405, 405]
    # Initialize an empty kernel matrix
    total_graphs = 4032
    complete_kernel_matrix = np.zeros((total_graphs, total_graphs))

    # List of all graph files
    list_of_files = glob.glob('v2/graphs/*/*.graphml')
    file_subsets = np.array_split(list_of_files, n_subsets)
    # Files with no nodes to be removed
    files_with_no_nodes = [
        'v2/graphs/Technology/learnmachinelearning.json.graphml',
        'v2/graphs/Technology/DataHoarder.json.graphml',
        'v2/graphs/Technology/talesfromtechsupport.json.graphml',
        'v2/graphs/Technology/technews.json.graphml',
        'v2/graphs/Technology/apolloapp.json.graphml',
        'v2/graphs/Technology/ipad.json.graphml',
        'v2/graphs/Technology/onions.json.graphml',
        'v2/graphs/Technology/Windows10.json.graphml',
        'v2/graphs/Art/AnalogCommunity.json.graphml',
        'v2/graphs/Art/iWallpaper.json.graphml',
        'v2/graphs/Art/ImaginaryHorrors.json.graphml',
        'v2/graphs/Art/pic.json.graphml',
        'v2/graphs/Art/ArtHistory.json.graphml',
        'v2/graphs/Art/80s.json.graphml',
        'v2/graphs/Art/Pyrography.json.graphml',
        'v2/graphs/Art/blenderhelp.json.graphml',
        'v2/graphs/Art/MobileWallpaper.json.graphml',
        'v2/graphs/Art/wallpaperengine.json.graphml'
    ]

    # Remove files with no nodes
    list_of_files = [file for file in list_of_files if file not in files_with_no_nodes]

    # remove files with no nodes from the subsets
    for i in range(n_subsets):
        file_subsets[i] = [file for file in file_subsets[i] if file not in files_with_no_nodes]
        print(f'Subset {i} has {len(file_subsets[i])} files')

    #dict of file to (subset, index)
    file_to_index = {}
    for i in range(n_subsets):
        for j, file in enumerate(file_subsets[i]):
            file_to_index[file] = (i, j)

        
    kernel_matrices = {}
    # load all kernel matrices
    for i, j in combinations(range(n_subsets), 2):
        kernel_matrix = load_kernel_matrix(f'v2/kernel_matrices/kernel_matrix_{i}_{j}.pkl')
        kernel_matrices[(i, j)] = kernel_matrix

    logging.info('Loaded all kernel matrices')

    # merge the kernel matrices
    for i in range(len(list_of_files)):
        for j in range(len(list_of_files)):
            if i == j or i > j:
                continue
            # logging.info(f'Processing {i} and {j}')
            file_i = list_of_files[i]
            file_j = list_of_files[j]
            subset_i, index_i = file_to_index[file_i]
            subset_j, index_j = file_to_index[file_j]

            print(f'Processing {i} and {j} with subsets {subset_i} and {subset_j}')
            # load kernel matrix of subset_i and subset_j
            if subset_i == subset_j:
                if subset_i < 9:
                    kernel_matrix = kernel_matrices[(subset_i, subset_i + 1)]
                    complete_kernel_matrix[i, j] = kernel_matrix[index_i, index_j]
                    complete_kernel_matrix[j, i] = complete_kernel_matrix[i, j]
                else:
                    kernel_matrix = kernel_matrices[(0, subset_i)]
                    complete_kernel_matrix[i, j] = kernel_matrix[(sizes[subset_i] - 1) + index_i, (sizes[subset_i] - 1) + index_j]
                    complete_kernel_matrix[j, i] = complete_kernel_matrix[i, j]
                continue
            elif subset_i < subset_j:
                kernel_matrix = kernel_matrices[(subset_i, subset_j)]
            else:
                kernel_matrix = kernel_matrices[(subset_j, subset_i)]

            complete_kernel_matrix[i, j] = kernel_matrix[index_i, (sizes[subset_i] - 1) + index_j]
            complete_kernel_matrix[j, i] = complete_kernel_matrix[i, j]

    # main diagonal = 1
    np.fill_diagonal(complete_kernel_matrix, 1)

    return complete_kernel_matrix

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    # Merge the matrices and save the complete kernel matrix
    complete_kernel_matrix = merge_kernel_matrices()
    with open('complete_kernel_matrix.pkl', 'wb') as f:
        pickle.dump(complete_kernel_matrix, f)
    logging.info('Saved complete kernel matrix')