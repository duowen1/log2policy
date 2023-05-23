import util


class Node:
    # self.name              <string>
    # self.versions          <dict>  dict[string]<Version>          : the sons of this service
    # self.edges             <set>   set[Edge]                      : who calls this service
    # self.update_versions   <set>   set[(attribute)]
    # self.flag              <bool>  true = new, false = old
    def __init__(self, name):
        self.name = name
        self.versions = dict()
        self.edges = set()  # who calls this service
        self.update_versions = set()
        self.flag = False

    def set_flag(self, flag = True):
        self.flag = True

    def is_new(self):
        return self.flag

    def add_version(self, version):
        self.versions[version.name] = version
        version.attach_service(self)

    def add_edge(self, edge):
        self.edges.add(edge)

    def dump_paths(self, filepath):
        path_set = set()
        for edge in self.edges:
            for attribute in edge.attributes:
                if attribute[-1] != "":
                    path_set.add(attribute[-1])

        with open(filepath, "w") as f:
            for path in path_set:
                if path is not None:
                    f.write(path+'\n')

    def find_wildcard(self, group_list, vocabulary_dict, special_words):
        for edge in self.edges:
            temp_attributes = edge.attributes.copy()
            edge.attributes = set()
            # for each traffic in this edge
            for element in temp_attributes:
                path = element[-1]
                if path != "":
                    path_fields = util.split_path(path)
                    # for each field in the path, check whether it is a wildcard
                    for field in path_fields:
                        if field != '' and not field.isnumeric():
                            try:
                                field_label = vocabulary_dict[field.lower()]
                            except KeyError:
                                print("KeyError", path_fields)
                            if field.lower() not in special_words and len(group_list[field_label]) >= 5:
                                # >=5 means that it should be replaced
                                path = path.replace(field, "*")

                # print(path)
                edge.attributes.add((element[0], element[1], element[2], element[3], element[4], element[5], path))


    def show(self):
        print("-----------------------------------------------------")
        print(self.name)

        for edge in self.edges:
            print(edge.source_version.service.name, edge.source_version.name, "--->", self.name)

        print(self.name, ":")
        for version_name, version_node in self.versions.items():
            print(version_name, ":")
            version_node.show()


    def dump2json(self):
        pass


class Version:
    # self.name       <string>
    # self.service    <Node>
    # self.edges      <set>        set[Edge]
    def __init__(self, name):
        self.service = None
        self.name = name
        self.edges = set()

    def attach_service(self, service):
        self.service = service

    def add_edge(self, edge):
        self.edges.add(edge)

    def show(self):
        for edge in self.edges:
            print(self.name, "-->", edge.destination.name)
            edge.show()


class Edge:
    # self.source             <Node>
    # self.source_version     <Version>
    # self.destination        <Node>
    # self.attributes         <set>        set[tuple]    tuple (source, version, destination, port, method, protocol, path)
    def __init__(self, source, source_version, destination):
        self.source = source
        self.source_version = source_version
        self.destination = destination
        self.attributes = set()

    def add_attribute(self, attribute):
        if attribute not in self.attributes:
            self.attributes.add(attribute)
            self.source.update_versions.add(attribute)

    def show(self):
        for attribute in self.attributes:
            print(attribute)

