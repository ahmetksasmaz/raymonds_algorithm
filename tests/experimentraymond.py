import os
import argparse

def execute_command(n, m, M, p, r, s):
    os.command("python3 testraymond.py -n {n_} -m {m_} -M {M_} -p {p_} -r {r_} -s {s_}".format(n_=n, m_=m, M_=M, p_=p, r_=r, s_=s))

def main():
    parser = argparse.ArgumentParser(description='Raymond\'s Algorithm Experimenter')
    parser.add_argument('-a','--all', help='Do all experiments', action="store_true")
    parser.add_argument('-k','--kary-tree', help='Do k-ary tree experiment', action="store_true")
    parser.add_argument('-c','--child-ratio', help='Do child ratio experiment', action="store_true")
    parser.add_argument('-m','--message-complexity', help='Do message complexity experiment', action="store_true")
    parser.add_argument('-N','--experiment-count', help='Experiment sample count for Monte Carlo Simulation', required=True, type=int)
    args = vars(parser.parse_args())

    pass

if __name__ == "__main__":
    main()