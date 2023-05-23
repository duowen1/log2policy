import numpy as np
from sklearn import cluster
from sklearn import metrics
import learning


def train_dbscan_metrics(samples, vocabulary, labels_true, eps=0.3, min_samples=1):
    dbscan = cluster.DBSCAN(
        eps=eps,
        min_samples=min_samples)
    dbscan.fit(samples)
    labels = dbscan.labels_.astype(int)

    homogeneity = metrics.homogeneity_score(labels_true, labels)
    completeness = metrics.completeness_score(labels_true, labels)
    v_measure = metrics.v_measure_score(labels_true, labels)

    print("homogeneity", homogeneity)
    print("completeness", completeness)
    print("V-measure", v_measure)


def train_dbscan(samples, vocabulary, servicename, eps=0.3, min_samples=1):
    dbscan = cluster.DBSCAN(
        eps=eps,
        min_samples=min_samples)
    dbscan.fit(samples)
    labels = dbscan.labels_.astype(int)

    with open("%s-dbscan_label" % servicename, "w") as f:
        # print(vocabulary,labels)
        index = 0
        for word in vocabulary:
            f.write("%s %d\n" % (word, labels[index]))
            index += 1

    return labels

    # for index in range(len(labels)):
    #     print(labels[index], vocabulary[index])

    labels_true = []
    homogeneity = metrics.homogeneity_score(labels_true, labels)
    completeness = metrics.completeness_score(labels_true, labels)
    v_measure = metrics.v_measure_score(labels_true, labels)


def train(servicename, samples, vocabulary, metric_flag=False, eps=0.3):
    if metric_flag:

        labels_true = load_labels(vocabulary, servicename)

        train_dbscan_metrics(samples, vocabulary, labels_true)
    return train_dbscan(samples, vocabulary, servicename, eps)


def load_labels(vocabulary, servicename):
    vocabulary_dict = dict()
    path = "your path"
    with open(path + "/%s-vocabulary" % servicename) as f:
        l = f.read()
        lines = l.split('\n')
        for line in lines:
            word = line.split(" ")[0]
            try:
                label = line.split(" ")[1]
            except IndexError:
                print(servicename, line)

            vocabulary_dict[word] = label

    true_label = []
    for word in vocabulary:
        true_label.append(vocabulary_dict[word])

    return true_label


def calculate_metrics(namespace, servicename):
    path = "your path"
    file_path = path + "/%s/%s" % (namespace, servicename)

    vocabulary_dict = dict()

    with open(file_path + "vocabulary", "r") as f:
        lines = f.read().split('\n')
        for line in lines:
            word = line.split(" ")[0]
            label = line.split(" ")[1]
            vocabulary_dict[word] = label

    # real label
    labels_true = []
    # labels
    labels = []
    with open(file_path + "dbscan_label") as f:
        lines = f.read().split("/n")
        for line in lines:
            word, label = line.split(' ')[0], line.split(' ')[1]

            labels_true.append(vocabulary_dict[word])
            labels.append(label)

    homogeneity = metrics.homogeneity_score(labels_true, labels)
    completeness = metrics.completeness_score(labels_true, labels)
    v_measure = metrics.v_measure_score(labels_true, labels)

    print(namespace, servicename)
    print("homo", homogeneity)
    print("complete", completeness)
    print("V-measure", v_measure)
