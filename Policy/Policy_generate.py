import util
import os
import graph.data_struct
from ruamel import yaml
import Policy.consise_rules as cs


def policy_generator(namespace, Services):
    util.mkdir_and_chdir("yaml")

    dump_to_file(peer_authentication(namespace), "peerauthentication.yaml")

    for service in Services.values():
        policies = authorization(namespace, service)
        dump_to_file(policies, service.name+".yaml")


def authorization(namespace, service):
    service_name = service.name

    authorizations = dict()

    authorizations["kind"] = "AuthorizationPolicy"
    authorizations["apiVersion"] = "security.istio.io/v1beta1"
    metadata = dict()
    authorizations["metadata"] = metadata
    spec = dict()
    authorizations["spec"] = spec

    # authorization.metadata
    metadata["name"] = service_name
    metadata["namespace"] = namespace

    # authorization.spec
    selector = dict()
    spec["selector"] = selector
    spec["action"] = "ALLOW"
    rules = []

    # authorization.spec.selector
    # if service_version == "":
    #     selector["matchLabels"] = {"app": service_name}
    # else:
    #     selector["matchLabels"] = {"app": service_name,
    #                                "version": service_version}

    selector["matchLabels"] = {"app": service_name}


    # for edge in service.edges:
    #     for attribute in edge.attributes:
    #         rules.append(
    #             make_rules(
    #                 namespace,
    #                 service_name,
    #                 attribute))

    rules += cs.preprocess_and_analyze(namespace, service_name, service.edges)

    if len(rules) != 0:
        rules.append(add_new_namespace())
    else:
        rules.append(dict())

    spec["rules"] = rules
    return authorizations


def add_new_namespace():
    rule = dict()
    from_list = []
    rule["from"] = from_list
    operation = dict()
    from_dict = dict()
    source = dict()
    from_dict["source"] = source
    namespaces = ["new"]
    source["namespaces"] = namespaces
    from_list.append(from_dict)
    return rule


def peer_authentication(namespace):
    policy = dict()

    policy["apiVersion"] = "security.istio.io/v1beta1"
    policy["kind"] = "PeerAuthentication"
    policy["metadata"] = {"name": "default", "namespace": namespace}

    spec = dict()
    policy["spec"] = spec
    spec["mtls"] = {"mode": "STRICT"}

    return policy


def dump_to_file(yaml_dict, filepath):
    print(filepath)
    with open(filepath, "w") as f:
        yaml.dump(yaml_dict, f, Dumper=yaml.RoundTripDumper)


def make_rules(namespace, service_name, attribute):
    service_account = namespace + "-" + attribute[0]

    method = attribute[4]
    path = attribute[-1]
    port = attribute[3]
    version = attribute[1]

    rules = dict()

    from_list = []
    to_list = []

    rules["from"] = from_list
    rules["to"] = to_list

    to_dict = dict()
    operation = dict()
    to_dict["operation"] = operation

    if method is not None:
        operation["methods"] = [method]

    if path is not None:
        operation["paths"] = [path]

    if port is not None:
        operation["ports"] = [port]

    to_list.append(to_dict)

    from_dict = dict()
    source = dict()
    from_dict["source"] = source
    namespaces = [namespace]
    source["namespaces"] = namespaces


    # TODO

    source["principals"] = ["cluster.local/ns/%s/sa/%s-%s" % (namespace, service_account, version)]
    from_list.append(from_dict)

    return rules


if __name__ == '__main__':
    os.chdir("../result/book-info")
    policy_generator("book-info")

