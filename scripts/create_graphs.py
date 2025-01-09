import datetime
import glob
import json
import os
from typing import Dict, List

import click
import networkx as nx
from textblob import TextBlob

def add_or_update_edge(G, source, target, sentiment_score):
    if G.has_edge(source, target):
        G[source][target]["weight"] += abs(sentiment_score)
    else:
        G.add_edge(source, target, weight=abs(sentiment_score))

def add_comments_to_graph(G, comments, parent_user):
    for comment in comments:
        commenter = comment["user"]
        G.add_node(commenter)
        blob = TextBlob(comment["body"])
        sentiment_score = blob.sentiment.polarity
        add_or_update_edge(G, parent_user, commenter, sentiment_score)
        if comment.get("replies"):
            add_comments_to_graph(G, comment["replies"], commenter)

def get_time_slice_key(timestamp, time_slice):
    dt = datetime.datetime.fromtimestamp(timestamp)
    if time_slice == 'day':
        return dt.date()
    elif time_slice == 'hour':
        return dt.replace(minute=0, second=0, microsecond=0)
    elif time_slice == 'week':
        return dt.isocalendar()[0:2]  # Year and week number
    else:
        return dt

def normalize_weights(G):
    try:
        weights = [data["weight"] for _, _, data in G.edges(data=True)]
        max_weight = max(weights)
        min_weight = min(weights)
        for _, _, data in G.edges(data=True):
            data["weight"] = (data["weight"] - min_weight) / (max_weight - min_weight) if max_weight != min_weight else 1
    except Exception as e:
        print(e)

def convert_to_graph(all_data, time_slice):
    graphs = {}
    for subreddit, data in all_data.items():
        subreddit_graphs = {}
        for entry in data:
            slice_key = get_time_slice_key(entry["post_time"], time_slice)
            if slice_key not in subreddit_graphs:
                subreddit_graphs[slice_key] = nx.DiGraph()
            G = subreddit_graphs[slice_key]
            G.add_node(entry["post_user"])
            post_blob = TextBlob(entry["post_body"])
            post_sentiment_score = post_blob.sentiment.polarity
            G.nodes[entry["post_user"]]["sentiment"] = post_sentiment_score
            add_comments_to_graph(G, entry["comments"], entry["post_user"])
            normalize_weights(G)
        graphs[subreddit] = subreddit_graphs
    return graphs

def get_json_files(path: str) -> Dict[str, List[str]]:
    files = glob.glob(f"{path}/*.json")
    data = {}
    for file in files:
        with open(file) as f:
            data[f.name.split('/')[-1].split('.')[0]] = json.load(f)
    # print(data.keys())
    return data

def save_graphs(graphs, output_path):
    for subreddit, dates_graphs in graphs.items():
        subreddit_path = os.path.join(output_path, subreddit)
        os.makedirs(subreddit_path, exist_ok=True)
        for date, graph in dates_graphs.items():
            graphml_path = os.path.join(subreddit_path, f"{date}.graphml")
            nx.write_graphml(graph, graphml_path)

@click.command()
@click.option('-p', '--path', prompt='Path to data directory', help='Path to data directory')
@click.option('-ts', '--time-slice', default='day',required=True, help='Create graphs for a time slice (hr/day/week)')
@click.option('-o', '--output', default='graphs', prompt='Output directory', help='Output directory')
def create_graphs(path, time_slice, output):
    all_data = get_json_files(path)
    graphs = convert_to_graph(all_data, time_slice)
    save_graphs(graphs, output)

if __name__ == '__main__':
    create_graphs()
