import os
import argparse
import random
import tqdm

def execute_command(n, m, M, p, r, s):
    os.system("python3 testraymond.py -n {n_} -m {m_} -M {M_} -p {p_} -r {r_} -s {s_}".format(n_=n, m_=m, M_=M, p_=p, r_=r, s_=s))

def kary_tree_experiment(N, force_exp_n = None):
    print("K-Ary Tree Experiment")
    for x in tqdm.tqdm(range(N)):
        if not force_exp_n:
            for exp_n in tqdm.tqdm(range(8)):
                for k in tqdm.tqdm(range(16)):
                    for exp_p in tqdm.tqdm(range(10)):
                        execute_command(2**(exp_n+1), k, k, 2**exp_p, 2**(exp_p+6), 0.000005) # Trigger all in 1000/2^6 ms, use critical section for 5us
        else:
            for k in tqdm.tqdm(range(16)):
                    for exp_p in tqdm.tqdm(range(10)):
                        execute_command(2**(force_exp_n+1), k, k, 2**exp_p, 2**(exp_p+6), 0.000005) # Trigger all in 1000/2^6 ms, use critical section for 5us

def child_ratio_experiment(N, force_exp_n = None):
    print("Child Ratio Experiment")
    for x in tqdm.tqdm(range(N)):
        if not force_exp_n:
            for exp_n in tqdm.tqdm(range(8)):
                for k_max in tqdm.tqdm(range(6)):
                    for k_min in tqdm.tqdm(range(2**k_max)):
                        for exp_p in tqdm.tqdm(range(10)):
                            execute_command(2**(exp_n+1), k_min+1, 2**k_max, 2**exp_p, 2**(exp_p+6), 0.000005) # Trigger all in 1000/2^6 ms, use critical section for 5us
        else:
            for k_max in tqdm.tqdm(range(6)):
                    for k_min in tqdm.tqdm(range(2**k_max)):
                        for exp_p in tqdm.tqdm(range(10)):
                            execute_command(2**(force_exp_n+1), k_min+1, 2**k_max, 2**exp_p, 2**(exp_p+6), 0.000005) # Trigger all in 1000/2^6 ms, use critical section for 5us

def message_complexity_experiment(N, force_exp_n = None):
    print("Message Complexity Experiment")
    for x in tqdm.tqdm(range(N)):
        if not force_exp_n:
            for exp_n in tqdm.tqdm(range(8)):
                k_max = random.randint(1,32)
                k_min = random.randint(1,k_max)
                for exp_p in tqdm.tqdm(range(10)):
                    execute_command(2**(exp_n+1), k_min, k_max, 2**exp_p, 2**(exp_p+6), 0.000005) # Trigger all in 1000/2^6 ms, use critical section for 5us
        else:
            k_max = random.randint(1,32)
            k_min = random.randint(1,k_max)
            for exp_p in tqdm.tqdm(range(10)):
                execute_command(2**(force_exp_n+1), k_min, k_max, 2**exp_p, 2**(exp_p+6), 0.000005) # Trigger all in 1000/2^6 ms, use critical section for 5us

def main():
    parser = argparse.ArgumentParser(description='Raymond\'s Algorithm Experimenter')
    parser.add_argument('-a','--all', help='Do all experiments', action="store_true")
    parser.add_argument('-k','--kary-tree', help='Do k-ary tree experiment', action="store_true")
    parser.add_argument('-c','--child-ratio', help='Do child ratio experiment', action="store_true")
    parser.add_argument('-m','--message-complexity', help='Do message complexity experiment', action="store_true")
    parser.add_argument('-n', '--force-number-of-nodes', help='Specifically initialize exp(n+1) nodes', required=False, type=int)
    parser.add_argument('-N','--experiment-count', help='Experiment sample count for Monte Carlo Simulation', required=True, type=int)
    args = vars(parser.parse_args())

    do_kary_tree_experiment = False
    do_child_ratio_experiment = False
    do_message_complexity_experiment = False
    force_exp_n = None
    if args["all"] == True:
        do_kary_tree_experiment = True
        do_child_ratio_experiment = True
        do_message_complexity_experiment = True
    else:
        do_kary_tree_experiment = args["kary_tree"]
        do_child_ratio_experiment = args["child_ratio"]
        do_message_complexity_experiment = args["message_complexity"]

    if do_kary_tree_experiment == False and do_child_ratio_experiment == False and do_message_complexity_experiment == False:
        print("Nothing to experiment.")
        exit()

    if args["experiment_count"] < 1:
        print("Experiment count must be greater than 0.")
        exit()

    if args["force_number_of_nodes"]:
        force_exp_n = args["force_number_of_nodes"]
        if force_exp_n < 0:
            print("Invalid node exponent.")
            exit()

    if do_kary_tree_experiment == True:
        kary_tree_experiment(args["experiment_count"], force_exp_n)
    if do_child_ratio_experiment == True:
        child_ratio_experiment(args["experiment_count"], force_exp_n)
    if do_message_complexity_experiment == True:
        message_complexity_experiment(args["experiment_count"], force_exp_n)

if __name__ == "__main__":
    main()