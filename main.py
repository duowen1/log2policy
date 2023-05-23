import time
import argparse
import util
import learning.learning as l
import graph.make_graph as graph_dump
import Policy.Policy_generate as pg

from preprocess import get_log_from_file
from preprocess import get_log_from_istio_proxy
from graph.make_graph import make_graph_from_traffic_and_dump_path


def main(namespace, concurrent_flag, percent, output):
    # make dir ./result/<namespace>
    if util.mkdir_and_chdir():
        util.mkdir_and_chdir(namespace)

    start = time.time()

    # -------------------------------------------------------------
    # Data Per-processing and Topology Generation

    Services, Edges = make_graph_from_traffic_and_dump_path(
        get_log_from_file(namespace,
                                 concurrent_flag,
                                 "istio-proxy",
                                 percent))

    log_collect_time = time.time()
    print("Topology Generation", log_collect_time - start)

    # ------------------------------------------------------------
    # Attributes Mining

    for service in Services.values():
        # split the path and label the path
        print("-----------------------------------")
        print("Analyzing", service.name)
        labels = l.learning(service.name)

        if labels is not None:
            group_list, vocabulary_dict, special_words = labels[0], labels[1], labels[2]
            service.find_wildcard(group_list, vocabulary_dict, special_words)

    # dump the graph after variable identification
    if output:
        graph_dump.dump_to_file(Services, namespace, False)

    learning_time = time.time()
    print("Attributes Mining", learning_time - log_collect_time)

    # ------------------------------------------------------------
    # Optimization

    pg.policy_generator(namespace, Services)

    policy_generate_time = time.time()
    print("generate time:", policy_generate_time - learning_time)

    # ------------------------------------------------------------
    end = time.time()
    print("total time:", end - start)


# Main entrance of the project
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get the envoy log from istio-proxy and generate access control '
                                                 'Policies')

    parser.add_argument('--namespace', '-n', type=str, default="default", help='an string for the namespace')
    parser.add_argument('--concurrent', '-c', type=bool, default=False, help='use multiprocess to accelerate')
    parser.add_argument('--database', '-d', type=bool, default=False, help='use database to store data')
    parser.add_argument('--percent', '-p', type=int, default=1, help='set sampling rate = 1/p, default no sampling')
    parser.add_argument('--output', '-o', type=bool, default=False, help='whether generate graph')
    args = parser.parse_args()

    main(args.namespace, args.concurrent, args.percent, args.output)
