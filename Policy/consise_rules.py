import copy
import Policy.Policy_generate as pg
import fnmatch


# Functions:
#   judge whether we need to generate
# Args:
#   namespace: String, the namespace of the application
#   concurrent_flag: Bool, use multiprocess to accelerate or not
#   container_name: String, the name of container whose log will be analyzed
# Returns:
#   traffics: A dictionary List, contains all the traffic in the application


def generate_vs_configuration(service_name, rule_list, exact_list):
    virtual_service = dict()

    virtual_service["apiVersion"] = "networking.istio.io/v1alpha3"
    virtual_service["kind"] = "VirtualService"
    virtual_service["metadata"] = {"name": service_name + "-route"}

    spec = dict()
    virtual_service["spec"] = spec

    spec["hosts"] = [service_name]

    route, fault = dict(), dict()
    http = [route, fault]
    spec["http"] = http

    percentage = {"value": 100.0}
    abort = {"percentage": percentage, "httpStatus": 400}
    fault["fault"] = {"abort": abort}
    fault["name"] = "fault-route"
    destination = {"host": service_name}
    fault["route"] = [{"destination": destination}]

    route_destination = copy.deepcopy(destination)
    route["name"] = service_name + "-route"
    route["route"] = [{"destination": route_destination}]

    match = []
    route["match"] = match

    # rule = (regex, method)
    for rule in rule_list:
        uri = {"regex": rule[0]}
        method = {"exact": rule[1]}
        match.append({"uri": uri, "method": method})

    for exact in exact_list:
        uri = {"exact": exact[0]}
        method = {"exact": exact[1]}
        match.append({"uri": uri, "method": method})

    pg.dump_to_file(virtual_service, service_name + "vs.yaml")


def preprocess_and_analyze(namespace, service_name, edges):
    regex_list = []
    exact_list = []
    authorization_list = []
    for edge in edges:
        rules_set = set()

        for attribute in edge.attributes:
            path = attribute[-1]
            if path is not None:
                index = path.find("*")
                if index != -1:
                    path_regex = path[:]
                    path_regex = path_regex.replace("*", "[^\\f\\n\\r\\t\\v/+?%#&=]+")
                    path_regex = "^%s$" % path_regex
                    # print(attribute)
                    method = attribute[4]
                    regex_list.append((path_regex, method.upper()))
                    path = path[:index + 1]
                else:
                    method = attribute[4]
                    exact_list.append((path, method.upper()))

            rules_set.add((attribute[0], attribute[1], attribute[2], attribute[3], attribute[4], attribute[5], path))


        for attribute in rules_set:
            flag = True
            path = attribute[-1]
            for f in rules_set:
                if f != attribute:
                    if f[2] == attribute[2] \
                            and f[4] == attribute[4] \
                            and f[-1] is not None \
                            and fnmatch.fnmatch(path, f[-1]):
                        flag = False
                        break
            if flag:
                authorization_list.append(pg.make_rules(namespace, service_name, (attribute[0], attribute[1], attribute[2], attribute[3], attribute[4], path)))

    if len(regex_list) > 0:
        generate_vs_configuration(service_name, regex_list, exact_list)

    return authorization_list


if __name__ == "__main__":
    rule_list = [("^/carts/[0-9a-f]{24}/items/[0-9a-zA-Z-]{36}$", "DELETE"),
                 ("^/carts/[0-9a-f]{24}/merge$", "GET"),
                 ("^/carts/[0-9a-f]{24}/items$", "GET"),
                 ("^/carts/[0-9a-f]{24}/items$", "POST"),
                 ("^/carts/[0-9a-f]{24}$", "DELETE")]
    generate_vs_configuration("carts", rule_list)
