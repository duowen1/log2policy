import argparse
import json
import time
import graph.data_struct as graph_ds
import log_preprocess as loganalyze
import Policy.Policy_generate as pg
import learning.learning as l

def load_graph(namespace):
    requests = 0


    path = "your path"
    file_name = path + "/check%s.json" % namespace

    Services = dict()
    path_dict = dict()

    with open(file_name, "r") as fd:
        service_json = fd.read()

    service_dict = json.loads(service_json)["Service"]

    for service in service_dict:
        service_node = graph_ds.Node(service["name"])

        for version in service["versions"]:
            version_node = graph_ds.Version(version["name"])
            version_node.attach_service(service_node)

            service_node.add_version(version_node)

        Services[service["name"]] = service_node

    for service in service_dict:
        path_list = []

        service_node = Services[service["name"]]

        for version in service["versions"]:
            version_node = service_node.versions[version["name"]]

            for edge in version["edges"]:
                edge_class = graph_ds.Edge(service_node, version_node, Services[edge["destination_name"]])

                for attr in edge["attributes"]:
                    requests += 1
                    attribute_tuple = (service["name"], version["name"], edge["destination_name"]) + tuple(attr.values())
                    if attribute_tuple[-1] is not None:
                        path_list.append(attribute_tuple[-1])
                        

                    edge_class.add_attribute(attribute_tuple)

                version_node.add_edge(edge_class)
                Services[edge["destination_name"]].add_edge(edge_class)
            path_dict[service["name"]] = path_list

    print(requests)
    # for service in Services.values():
    #     service.show()

    return Services, path_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='update the policies')
    parser.add_argument('--namespace', '-n', type=str, default="default", help='an string for the namespace')
    parser.add_argument('--percent', '-p', type=int, default=1, help='1 / percent sampling rate')
    args = parser.parse_args()

    start = time.time()

    # load topology graph from file
    Services, path_dict = load_graph(args.namespace)

    print(path_dict)

    # opt_1:read log file from istio proxy
    # traffics = loganalyze.get_log_from_istio_proxy(args.namespace, 1)

    # opt_2:read log file from disk
    traffics = loganalyze.get_log_from_file(args.namespace, 10)

    # print(traffics)

    # update the topological graph
    Services, Edges = loganalyze.upgrade_make_graph_from_traffic_and_dump_path(traffics, Services, path_dict)

    for service in Services.values():
        service.show()

    # Variable Identification
    for service in Services.values():
        # if from free namespace
        if service.is_new():
            labels = l.learning(service.name)

            if labels is not None:
                group_list, vocabulary_dict, special_words = labels[0], labels[1], labels[2]
                service.find_wildcard(group_list, vocabulary_dict, special_words)

    # Generate Rules
    pg.policy_generator(args.namespace, Services)

    end = time.time()
    print(end - start)
