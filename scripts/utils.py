import json
import os
from datetime import datetime
from typing import List, Dict, Any

import constants
import graph

def read_subreddits_from_txt(filename: str) -> List[str]:
    with open(filename) as f:
        urls = [x.strip() for x in f.readlines()]
    return [f"https://www.reddit.com/r/{i}/top/?t=month" for i in urls]

def save_to_json(category, data: List[Dict[str, Any]], subreddit: str) -> str:
    directory = f"{constants.DATA_DIR}/{category}"
    os.makedirs(directory, exist_ok=True)
    filename = f"{directory}/{subreddit}.json"
    with open(filename, "w") as f:
        json.dump(data, f)

def get_comments_replies(comment_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    comments_list = []
    for comment in comment_data:
        if comment["kind"] != "t1":
            continue
        comment_body = comment["data"]["body"]
        comment_user = comment["data"]["author"]
        comment_time = comment["data"]["created_utc"]
        comment_dict = {
            "body": comment_body,
            "user": comment_user,
            "time": comment_time,
            "replies": get_comments_replies(comment["data"]["replies"]["data"]["children"]) if comment["data"].get("replies") else []
        }
        comments_list.append(comment_dict)
    return comments_list

def get_post_info(json_data: Dict[str, Any]) -> Dict[str, Any]:
    post = json_data[0]["data"]["children"][0]["data"]
    post_body = post["title"]
    post_user = post["author"]
    post_time = post["created_utc"]
    comments_data = json_data[1]["data"]["children"]
    return {
        "post_body": post_body,
        "post_user": post_user,
        "post_time": post_time,
        "comments": get_comments_replies(comments_data)
    }

def saved_subreddits_in_txt(path: str) -> None:
    subdirs = [subdir for subdir in os.listdir(path) if os.path.isdir(os.path.join(path, subdir))]
    with open(constants.ALL_SCRAPED_FILE, "w") as f:
        for subdir in subdirs:
            f.write(subdir + "\n")

def read_subreddits_from_json(filename: str, duration) -> Dict[str, List[str]]:
    with open(filename) as f:
        data = json.load(f)

    for category in data:
        data[category] = [f"https://www.reddit.com/r/{i}/top/?t={duration}" for i in data[category]]
    return data

def save_graphs(subreddits: Dict[str, List[str]]) -> None:
    all_data = graph.load_all_jsons(subreddits)
    graphs = graph.convert_to_graph(all_data)
    # remove outlier graphs
    retained_graphs, removed_graphs = graph.remove_outliers(graphs)
    for category, graph_ in removed_graphs.items():
        print(f"Removed {category} {len(graph_)} graphs")
    graph.save_graphs(retained_graphs, subreddits)

# if __name__ == "__main__":
#     subreddits = read_subreddits_from_json(constants.SUBREDDITS_FILE, "month")
#     for category, urls in subreddits.items():
#         subreddits[category] = [url.split("/")[-3] for url in urls]
#     subreddits_ = []
#     for list in subreddits.values():
#         for subreddit in list:
#             subreddits_.append(subreddit)
#     print(subreddits_)
#     import glob
#     graphs = glob.glob(f"../new/data/*/*.json")
#     data = {}
#     for g in graphs:
#         if g.split("/")[-2] not in data:
#             data[g.split("/")[-2]] = []
#         if g.split("/")[-1].split(".")[0] not in subreddits_:
#             continue
#         with open(g) as f:
#             data[g.split("/")[-2]].append(json.load(f))
#     graphs = graph.convert_to_graph(data)
#     # retained_graphs, removed_graphs = graph.remove_outliers(graphs)
#     # for category, graph_ in removed_graphs.items():
#     #     print(f"Removed {category} {len(graph_)} graphs")
#     graph.save_graphs(graphs, subreddits)