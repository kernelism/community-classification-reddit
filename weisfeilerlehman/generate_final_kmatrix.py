from combination_kmatrix import *

TOTAL_GRAPHS = 4032
KERNEL_MATRICES_BP = "./kernel_matrices/"
GRAPHS_BP = "/Users/arjuns/Downloads/notebooks_v2/v2/graphs"

def load_kernel_matrix(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)
    
def get_sizes():
    sizes = [405, 405, 405, 405, 393, 399, 405, 405, 405, 405]
    return sizes
    
def merge_kernel_matrices(n_subsets=10):
    sizes = get_sizes()

    # Initialize an empty kernel matrix
    complete_kernel_matrix = np.zeros((TOTAL_GRAPHS, TOTAL_GRAPHS))

    # List of all graph files
    list_of_files = glob.glob(f'{GRAPHS_BP}/*/*.graphml')
    file_subsets = np.array_split(list_of_files, n_subsets)

    # Files with no nodes to be removed
    files_with_no_nodes = [
        f'{GRAPHS_BP}/Technology/learnmachinelearning.json.graphml',
        f'{GRAPHS_BP}/Technology/DataHoarder.json.graphml',
        f'{GRAPHS_BP}/Technology/talesfromtechsupport.json.graphml',
        f'{GRAPHS_BP}/Technology/technews.json.graphml',
        f'{GRAPHS_BP}/Technology/apolloapp.json.graphml',
        f'{GRAPHS_BP}/Technology/ipad.json.graphml',
        f'{GRAPHS_BP}/Technology/onions.json.graphml',
        f'{GRAPHS_BP}/Technology/Windows10.json.graphml',
        f'{GRAPHS_BP}/Art/AnalogCommunity.json.graphml',
        f'{GRAPHS_BP}/Art/iWallpaper.json.graphml',
        f'{GRAPHS_BP}/Art/ImaginaryHorrors.json.graphml',
        f'{GRAPHS_BP}/Art/pic.json.graphml',
        f'{GRAPHS_BP}/Art/ArtHistory.json.graphml',
        f'{GRAPHS_BP}/Art/80s.json.graphml',
        f'{GRAPHS_BP}/Art/Pyrography.json.graphml',
        f'{GRAPHS_BP}/Art/blenderhelp.json.graphml',
        f'{GRAPHS_BP}/Art/MobileWallpaper.json.graphml',
        f'{GRAPHS_BP}/Art/wallpaperengine.json.graphml'
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
        kernel_matrix = load_kernel_matrix(f'{KERNEL_MATRICES_BP}/kernel_matrix_{i}_{j}.pkl')
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

start_time = time.time()    
if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    complete_kernel_matrix = merge_kernel_matrices()
    end_time = time.time()  
    logging.info(f"Total time taken: {end_time - start_time}")
    with open('./final_kernel_matrix/complete_kernel_matrix_v3.pkl', 'wb') as f:
        pickle.dump(complete_kernel_matrix, f)
    logging.info('Saved complete kernel matrix')