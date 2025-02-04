
#  Supervised vs Unsupervised Learning Approaches to Topic Classification on Reddit Conversational Graphs

This project attempts to follow several (supervised & unsupervised) approaches towards topical classification on Reddit data that is modelled as a conversational graph. More on the data setup below. 

We strictly use *only* the network structure itself in our methods and have not leveraged the content for this study. 

**This project is part of a research paper that is still work-in-progress.**

## Data
The raw Reddit JSON data is structured like this.
- `id`: the post's unique identifier
- `post_user`: the post's author
- `post_time`: the time at which the post was created, in unix time
- `post_body`: the post's body
- `post_polarity`: the post's polarity, as a number between -1 and 1
- `post_sentiment`: the post's sentiment, 0 for neutral, 1 for positive, -1 for negative
- `comments`: a list of comments on the post, where each comment is a dictionary with the following keys:
  - `id`: the comment's unique identifier
  - `user`: the comment's author
  - `time`: the time at which the comment was created, in unix time
  - `body`: the comment's body
  - `comment_polarity`: the comment's polarity, as a number between -1 and 1
  - `comment_sentiment`: the comment's sentiment, 0 for neutral, 1 for positive, -1 for negative
  - `replies`: a list of replies to the comment, where each reply is a dictionary with the same keys as a comment

This was processed into a graph with the following rules:
- Every user is a node
- There is an edge between each comment owner to the post owner
- There is an edge between each reply owner to the comment owner.
- Edge weight representing the normalized sentiment score of all interactions between the two users in a specific direction. (This was done initially but the sentiment scores as such was not used in any of the research paths we followed).

These graphs will be referred to as `Level 1` graphs.

The raw dataset can be found [here](https://zenodo.org/records/13343578).

## Approaches

Both supervised and unsupervised techniques were explored. 

### Supervised
We trained a Graph Neural Network (GNN) to classify `Level 1` graphs, but due to the large graph sizes, we used [Graph2Vec](https://karateclub.readthedocs.io/en/latest/_modules/karateclub/graph_embedding/graph2vec.html) to embed these into 128-dimensional vectors. Graph2Vec leverages Weisfeiler-Lehman subtree kernels to capture structural features, which are then encoded into fixed-size embeddings. While this method simplifies computations, it may lose granular structural details.

Using the resulting embeddings, we created `Level 2` graphs where nodes represent Level 1 graphs, and edges connect nodes with cosine similarity scores above a chosen threshold. Threshold selection was critical and involved cross-validation to balance connectivity and sparsity.

![l1tol2.png](./results/l1tol2.png)

The GNN architecture and results are given below.

![gnnarch.png](./results/gnnarchitecture.png)

| ![Test Accuracy](./results/testacc.png) | ![Loss Curves](./results/losscurves3d.png) |
|----------------------------------------|--------------------------------------------|

Through cross-validation, we were able to achieve an `~84%` average test accuracy across folds, for `~200` graphs per label for a total of `13` labels.

We believe that, for a larger dataset, it should be possible to achieve better results.


### Unsupervised

#### Community and Overlapping Community Detection.
Since we had the `Level 2` graphs generated for different thresholds above, we tried to use them to use natural clustering algorithms, however, the threshold selection process did not turn up to as easy as the supervised example. We resorted to using KDE (Kernel Density Estimate), which was helpful for identifying potential thresholds as it smooths out the randomness in the distribution and highlights underlying patterns. Through KDE, we can locate potential inflection points.

| ![infpoints.png](./results/infpoints.png) | ![thredge.png](./results/thresholdedge.png) |
|----------------------------------------|--------------------------------------------|

Once we had the thresholds, we built the new `Level 2` graphs.

```
Initialize an empty dictionary `graphs`

For each `threshold` in `inflection_points`:
    Initialize an empty graph `G`

    # Add nodes to the graph
    For each `graph` in `level_1_graphs`:
        Add `graph` as a node to `G`

    # Add edges based on similarity matrix and threshold
    For `i` from 0 to (number of rows in similarity_matrix - 1):
        For `j` from (i + 1) to (number of columns in similarity_matrix):
            If `similarity_matrix[i][j]` > `threshold`:
                Add an edge between nodes `level_1_graphs[i]` and `level_1_graphs[j]`
                Assign weight = `similarity_matrix[i][j]`

    Store graph `G` in `graphs`
```

Once we have the graphs, we ran both community and overlapping community detection algorithms. 

Since we cannot really control the number of clusters returned, we decided to take a more democratised approach to validating the results in this case.

We used homogeneity, which takes into account the MCC (most common category) in any given community and calculates the **homogeneity** of that community. 

| ![homog.png](./results/homogeneity.png) | ![overlappinghomog.png](./results/homogeneity_OCD.png) |
|--------------------------------|--------------------------------|

When it comes to Overlapping communities, we weight the contribution based on how many communities a given node has been assigned. 

The results are provided below.
![CD](./results/all_outs.png)

![OCD](./results/ocd_all.png)

### What do these results mean? 
TBD

## Algorithm Performance Table

| Algorithm             | Threshold | Homogeneity | Modularity | Accuracy (GNN) | F1   | NMI   | ARI   |
|-----------------------|-----------|-------------|------------|----------------|------|-------|-------|
| Louvain               | 0.0096    | 0.7817      | 0.50       | N/A            | 0.50 | 0.53  | 0.46  |
| Label Propagation     | 0.0052    | 0.98        | 0.001      | N/A            | 0.79 | 0.788 | 0.58  |
| Fast Greedy           | 0.0071    | 0.9090      | 0.3506     | N/A            | 0.82 | 0.90  | 0.96  |
| Leading Eigenvector   | 0.0075    | 0.7648      | 0.3669     | N/A            | 0.73 | 0.70  | 0.45  |
| Walktrap              | 0.0096    | 0.9053      | 0.4060     | N/A            | 0.80 | 0.53  | 0.04  |
| Infomap               | 0.0096    | 0.844       | 0.462      | N/A            | 0.71 | 0.52  | 0.09  |
| Multilevel            | 0.0075    | 0.821       | 0.427      | N/A            | 0.37 | 0.635 | 0.65  |
| leiden                | 0.0047    | 0.748       | 0.365      | N/A            | 0.37 | 0.65  | 0.63  |
| SLPA                  | 0.0074    | 0.86        | 0.51       | N/A            | 0.5  | 0.64  | 0.44  |
| MultiCOM              | 0.0096    | 0.55        | -0.05      | N/A            | 0.15 | 0.34  | 0/38  |
| Angel                 | 0.0098    | 0.69        | -0.014     | N/A            | 0.56 | 0.41  | 0.02  |
| Demon                 | 0.0098    | 0.65        | 0.06       | N/A            | 0.61 | 0.39  | 0.05  |
| Core Expansion        | 0.0089    | 0.69        | 0.05       | N/A            | 0.68 | 0.39  | 0.03  |
| GNN                   | 0.11      | N/A         | N/A        | 84% (average)  | 0.90  | 0.90   | 0.84   |


## Cite
If you build upon or use our work in a scientific publication, please cite our paper - (https://hahaweaintpublishedyet.com/best-paper-of-2025)

```
@article{hahaweaintpublishedyet,
  author  = {Dayanand V, Arjhun Sreedar and Pranav Deepak},
  title   = {hahaweaintpublishedyet},
  journal = {Journal of hahaweaintpublishedyet},
  year    = {2025},
  volume  = {?},
  number  = {?},
  pages   = {?}
}
```

## Contributors
- [Dayanand V](mailto:v_dayanand@cb.amrita.edu)
- [Pranav Deepak](mailto:pranavdeepak13@gmail.com)
- [Arjhun Sreedar](mailto:contactarjhun@gmail.com)

