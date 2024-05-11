import pandas as pd
import argparse
import matplotlib.pyplot as plt

def plot_message_complexity(df, save_plots):
    plot = plt.figure()
    ax = plt.axes()
    ax.scatter(df["node"], df["message_per_privilege"])
    ax.set_xlabel("Node Count")
    ax.set_ylabel("Message Per Privilege Request")
    plt.show()
    if save_plots == True:
        plt.savefig("message_complexity.png")

def plot_child_ratio(df, save_plots):
    plot = plt.figure()
    ax = plt.axes(projection='3d')
    ax.scatter(df["node"], df["child_ratio"], df["message_per_privilege"])
    ax.set_xlabel("Node Count")
    ax.set_ylabel("Min / Max Child Ratio")
    ax.set_zlabel("Message Per Privilege Request")
    plt.show()
    if save_plots == True:
        plt.savefig("child_ratio.png")

def plot_kary_tree(df, save_plots):
    well_formed_df = df[df["min_child"] == df["max_child"]]
    plot = plt.figure()
    ax = plt.axes(projection='3d')
    ax.scatter(well_formed_df["node"], well_formed_df["min_child"], well_formed_df["message_per_privilege"])
    ax.set_xlabel("Node Count")
    ax.set_ylabel("K")
    ax.set_zlabel("Message Per Privilege Request")
    plt.show()
    if save_plots == True:
        plt.savefig("kary_tree.png")

def main():
    parser = argparse.ArgumentParser(description='Raymond\'s Algorithm Benchmark Parser')
    parser.add_argument('-f','--file', help='Benchmark file', default="benchmark_results.csv", required=False, type=str)
    parser.add_argument('-a','--all', help='Plot all benchmark results', action="store_true")
    parser.add_argument('-m','--message-complexity', help='Plot total message over privilege request count w.r.t. node count', action="store_true")
    parser.add_argument('-c','--child-ratio', help='Plot total message over privilege request count w.r.t. node count and min/max child ratio', action="store_true")
    parser.add_argument('-k','--kary-tree', help='Plot total message over privilege request count w.r.t. node count for well formed k-ary tree', action="store_true")
    parser.add_argument('-s','--save', help='Save plots', action="store_true")
    args = vars(parser.parse_args())

    plot_or_not_message_complexity = False
    plot_or_not_child_ratio = False
    plot_or_not_kary_tree = False
    save_plots = args["save"]
    if args["all"] == True:
        plot_or_not_message_complexity = True
        plot_or_not_child_ratio = True
        plot_or_not_kary_tree = True
    else:
        plot_or_not_message_complexity = args["message_complexity"]
        plot_or_not_child_ratio = args["child_ratio"]
        plot_or_not_kary_tree = args["kary_tree"]
    if plot_or_not_message_complexity == False and plot_or_not_child_ratio == False and plot_or_not_kary_tree == False:
        print("Nothing to plot.")
        exit()

    df = pd.read_csv(args["file"], dtype=float, names=[
        "node",
        "min_child",
        "max_child",
        "privilege",
        "total_want_privilege",
        "total_duplicate_want_privilege",
        "total_used_critical_section",
        "total_released_critical_section",
        "total_request_message_received",
        "total_token_message_received",
        "total_request_message_sent",
        "total_token_message_sent"
    ])


    df["total_message"] = df["total_request_message_sent"] + df["total_token_message_sent"]
    df["message_per_privilege"] = df["total_message"] / df["total_want_privilege"]
    df["child_ratio"] = df["min_child"] / df["max_child"]

    df = df.groupby(['node', 'min_child', 'max_child', 'total_want_privilege']).mean().reset_index()

    if plot_or_not_message_complexity == True:
        plot_message_complexity(df, save_plots)
    if plot_or_not_child_ratio == True:
        plot_child_ratio(df, save_plots)
    if plot_or_not_kary_tree == True:
        plot_kary_tree(df, save_plots)

if __name__ == "__main__":
    main()