import time
import graph.data_struct as ds
import json


# Functions:
# For every traffic we get from the log, make graph. For every service, we output its paths to file.
def make_graph_from_traffic_and_dump_path(traffics):
    # Services[service_name] = Node
    Services = dict()
    # Edges[edge_hash] = Edge
    Edges = dict()
    # start = time.time()

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
        else:
            destination_node = Services[destination_name]

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

    for svc in Services.values():
        svc.dump_paths(svc.name)

    # if we need raw traffic and raw graphs, then dump_to_file(Services) in json format
    # dump_to_file(Services)

    return Services, Edges


def dump_to_file(service, namespace="sock-shop", before_flag = True):
    filename = namespace + ".json"

    if not before_flag:
        filename = "check" + filename

    with open(filename, "w") as f:
        service_json = {
            "Service": []
        }
        for serv in service.values():
            serv_json = {
                "name": serv.name,
                "versions": []
            }

            for v in serv.versions.values():
                v_json = {
                    "name": v.name,
                    "edges": []
                }

                for e in v.edges:
                    e_json = {
                        "destination_name": e.destination.name,
                        "attributes": []
                    }

                    for a in e.attributes:
                        a_json = {
                            'port': a[3],
                            'method': a[4],
                            'protocol': a[5],
                            'path': a[6]
                        }
                        e_json["attributes"].append(a_json)

                    v_json["edges"].append(e_json)

                serv_json["versions"].append(v_json)

            service_json["Service"].append(serv_json)

        f.write(json.dumps(service_json, indent=4))
        f.write("\n")
