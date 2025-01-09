import glob
import json
import os
from typing import List, Dict, Any

import networkx as nx
import numpy as np
from textblob import TextBlob

import constants

def load_all_jsons(subreddits: Dict[str, List[str]]) -> Dict[str, List[Dict[str, Any]]]:
    all_data = {}
    for category in subreddits.keys():
        # find all files under DATA_DIR/category
        category_files = [x.split('/')[-3] for x in subreddits[category]]
        files = glob.glob(f"{constants.DATA_DIR}/{category}/*.json")
        all_data[category] = []
        for file in files:
            filename = file.split('/')[-1].split('.')[0]
            if filename not in category_files:
                continue
            with open(file) as f:
                data = json.load(f)
            all_data[category].append(data)

    for k,v in all_data.items():
        print(f"{k}: {len(v)}")
    return all_data

def add_or_update_edge(G: nx.Graph, source: str, target: str, sentiment_score: float) -> None:
    if G.has_edge(source, target):
        G[source][target]["weight"] += abs(sentiment_score)
    else:
        G.add_edge(source, target, weight=abs(sentiment_score))

def add_comments_to_graph(G: nx.Graph, comments: List[Dict[str, Any]], parent_user: str) -> None:
    for comment in comments:
        commenter = comment["user"]
        G.add_node(commenter)
        blob = TextBlob(comment["body"])
        sentiment_score = blob.sentiment.polarity
        add_or_update_edge(G, parent_user, commenter, sentiment_score)
        if comment.get("replies"):
            add_comments_to_graph(G, comment["replies"], commenter)

def convert_to_graph(all_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[nx.DiGraph]]:
    graphs = {}
    for category, data in all_data.items():
        graphs[category] = []
        for graph in data:
            G = nx.DiGraph()
            for user in graph:
                G.add_node(user["post_user"])
                post_blob = TextBlob(user["post_body"])
                post_sentiment_score = post_blob.sentiment.polarity
                G.nodes[user["post_user"]]["sentiment"] = post_sentiment_score
                add_comments_to_graph(G, user["comments"], user["post_user"])

            normalize_weights(G)
            graphs[category].append(G)
    return graphs

def normalize_weights(G: nx.Graph) -> None:
    try:
        weights = [data["weight"] for _, _, data in G.edges(data=True)]
        max_weight = max(weights)
        min_weight = min(weights)
        for _, _, data in G.edges(data=True):
            data["weight"] = (data["weight"] - min_weight) / (max_weight - min_weight) if max_weight != min_weight else 1
    except Exception as e:
        print(e)

def remove_outliers(graphs: Dict[str, List[nx.DiGraph]]):
    retained_graphs = {}
    removed_graphs = {}

    for category, graph_list in graphs.items():
        if len(graph_list) < 2:
            retained_graphs[category] = graph_list
            continue
        # Calculate the node counts for each graph
        node_counts = [graph.number_of_nodes() for graph in graph_list]

        # Calculate Q1, Q3, and IQR
        Q1 = np.percentile(node_counts, 25)
        Q3 = np.percentile(node_counts, 75)
        IQR = Q3 - Q1
        print(f"{category}: Q1={Q1}, Q3={Q3}, IQR={IQR}")
        # Filter out the graphs
        retained = []
        removed = []
        for graph in graph_list:
            node_count = graph.number_of_nodes()
            if node_count < Q1 - 1.5 * IQR or node_count > Q3 + 1.5 * IQR:
                removed.append(graph)
            else:
                retained.append(graph)

        retained_graphs[category] = retained
        removed_graphs[category] = removed

    return retained_graphs, removed_graphs

def save_graphs(graphs: Dict[str, List[nx.DiGraph]], subreddits: Dict[str, List[str]]) -> None:
    for category, graphs_list in graphs.items():
        # Ensure the category directory exists
        category_dir = os.path.join(constants.GRAPHS_DIR, category)
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)

        for i, graph in enumerate(graphs_list):
            # Construct the file path
            try:
                subreddit_name = subreddits[category][i].split('/')[-3]
                file_path = os.path.join(category_dir, f"{subreddit_name}.graphml")

                # Write the graph to the file
                nx.write_graphml(graph, file_path)
            except Exception as e:
                print(f"Error saving graph for {category}/{subreddit_name}: {e}")

