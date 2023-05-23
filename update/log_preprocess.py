from kubernetes import client, config
from preprocess import logs_to_traffics, traffics
import graph.data_struct as ds
import fnmatch

def get_log_from_file(namespace, percent):
    path = "your path"
    file_address = "your path" + "/evaluation/onlineboutique/update/"

    # file_list = ["orders-v2", "catalogue-v2", "shipping-v2"]

    # file_list = ["order-v2", "product-v2", "client-v1"]

    # file_list = ["adservice-v2", "currencyservice-v2", "emailservice-v2"]

    file_list = ["vehiclemanagementapi-v2", "workshopmanagementapi-v2", "customermanagementapi-v2"]

    for file in file_list:
        with open(file_address + file, "r") as f:
            logs = f.read()
            count = logs_to_traffics(logs, file + "-xxx-xxxx", percent)
            print(count)
    return traffics


def get_log_from_istio_proxy(namespace, percent):
    config.load_kube_config()
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace)

    for pod in pods.items:
        if "-v2-" in pod.metadata.name:
            print(pod.metadata.name)
            logs = v1.read_namespaced_pod_log(pod.metadata.name, namespace, container="istio-proxy")
            count = logs_to_traffics(logs, pod.metadata.name, percent)
            print(count)

    pods = v1.list_namespaced_pod('new')

    for pod in pods.items:
        logs = v1.read_namespaced_pod_log(pod.metadata.name, 'new', container="istio-proxy")
        count = logs_to_traffics(logs, pod.metadata.name, percent)

    return traffics


def upgrade_make_graph_from_traffic_and_dump_path(traffics, Services, path_dict):
    
    old_namespace_services = list(Services.keys())
    
    Edges = dict()

    for traffic in traffics:

        source_name = traffic["source"]
        version_name = traffic["version"]
        destination_name = traffic["destination"]

        # make source service node and source version node
        if source_name not in Services:
            service_node = ds.Node(source_name)
            Services[source_name] = service_node
            version_node = ds.Version(version_name)
            service_node.add_version(version_node)

        else:
            service_node = Services[source_name]
            if version_name not in service_node.versions:
                version_node = ds.Version(version_name)
                service_node.add_version(version_node)
            else:
                version_node = service_node.versions[version_name]

        # make destination service node
        if destination_name not in Services:
            destination_node = ds.Node(destination_name)
            Services[destination_name] = destination_node
            destination_node.set_flag()
        else:
            destination_node = Services[destination_name]

        # if is old service(not in free namespace)
        if not destination_node.is_new():
            if source_name in path_dict:
                path_list_old = path_dict[source_name]
                for paths in path_list_old:

                    if traffic["path"] is not None and fnmatch.fnmatch(traffic["path"], paths):
                        traffic["path"] = paths
                        break

        edge_hash = hash((source_name, version_name, destination_name))
        if edge_hash not in Edges:
            edge = ds.Edge(service_node, version_node, destination_node)
            Edges[edge_hash] = edge
            version_node.add_edge(edge)
            destination_node.add_edge(edge)
        else:
            edge = Edges[edge_hash]

        edge.add_attribute((traffic["source"],
                            traffic["version"],
                            traffic["destination"],
                            traffic["port"],
                            traffic["method"],
                            traffic["protocol"],
                            traffic["path"]))

        # Only dump free namespace path
        for svc in Services.keys():
            if svc not in old_namespace_services:
                Services[svc].dump_paths(svc)

    return Services, Edges