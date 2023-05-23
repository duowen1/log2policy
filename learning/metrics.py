from sklearn import metrics, decomposition, cluster
import numpy as np
import seaborn
from matplotlib import pyplot

def plot_graph():
    path = "your path"
    data = np.load(path + "/catalogue-skipgram.npz")['samples']


    with open(path + "/catalogue-skipgram") as f:
        vocabulary = f.read().split('\n')[:-1]

    dbscan = cluster.DBSCAN(
        eps=0.35,
        min_samples=1)
    dbscan.fit(data)
    labels = dbscan.labels_.astype(int)
    svd = decomposition.TruncatedSVD(n_components=2)
    pos = svd.fit_transform(data)

    x, y = pos[:, 0], pos[:, 1]
    plot = seaborn.scatterplot(x, y)

    color = ['red','blue','green','yellow','black', 'grey','purple','orange','pink']
    for i in range(0, len(vocabulary)):
        plot.text(x[i], y[i] + 2e-2, vocabulary[i], horizontalalignment='center', size='small',
                  color=color[labels[i]%9], weight='semibold')
    pyplot.show()

def calculate_metrics(namespace, servicename):
    path = "your path"
    file_path = "your path" + "/PycharmProjects/evaluation/result/%s/%s" % (namespace, servicename)

    vocabulary_dict = dict()

    with open(file_path + "-vocabulary", "r") as f:
        lines = f.read().split('\n')
        for line in lines:
            if line == "":
                continue
            word = line.split(" ")[0]
            try:
                label = line.split(" ")[1]
            except IndexError:
                print(line)
                exit(0)
            vocabulary_dict[word] = int(label)

    # real label
    labels_true = []
    # labels
    labels = []
    with open(file_path + "-dbscan_label") as f:
        lines = f.read().split("\n")
        for line in lines:
            try:
                word, label = line.split(' ')[0], line.split(' ')[1]
            except IndexError:
                print(file_path)

            labels_true.append(vocabulary_dict[word])
            labels.append(label)

    homogeneity = metrics.homogeneity_score(labels_true, labels)
    completeness = metrics.completeness_score(labels_true, labels)
    v_measure = metrics.v_measure_score(labels_true, labels)

    print(namespace, servicename)
    print("homo", homogeneity)
    print("complete", completeness)
    print("V-measure", v_measure)
    print("---")


if __name__ == '__main__':
    service_name_list = ["carts", "catalogue", "user"]
    for service in service_name_list:
        calculate_metrics("sock-shop", service)