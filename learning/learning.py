import util
import os
import numpy as np
import learning.word2vec as w2v
import learning.clustering as cluster
import argparse 
# import word2vec as w2v
# import clustering as cluster


def learning_file(file_path, dim=5, radius=0.3):
    with open(file_path) as f:
        corpus = f.readlines()
        if len(corpus) < 10:
            print("need not to learn")
            return None
        path_list = []
        # path_split_list = []

        # split the URL-path
        special_words = set()
        for path in corpus:
            path = util.split_path(path)
            # path_split_list.append(path)
            if len(path) == 1:
                special_words.add(path[0])
            path_list.append(' '.join(path))

        # print(special_words)
        samples, vocabulary = w2v.main(path_list, dim)

        path = "your path"

        with open(path + "%s-skipgram" % file_path, "w") as fd:
            for word in vocabulary:
                fd.write(word+'\n')

        np.savez(path + "/%s-skipgram" % file_path, samples=samples)


        if samples is not None:
            labels = cluster.train(file_path, samples, vocabulary, False, radius)
            # w2v.show_picture(samples, vocabulary, labels)
            group_list, vocabulary_dict = util.group_by(labels, list(vocabulary))

            return group_list, vocabulary_dict, special_words
        else:
            return None


def learning(service_name, dim=5, radius=0.3):
    return learning_file(service_name, dim, radius)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='different learning argument')

    parser.add_argument('--dim', '-d', type=int, default=5)
    parser.add_argument('--radius', '-r', type=float, default=0.3)

    args = parser.parse_args()

    services = ['carts', 'catalogue', 'orders', 'user']

    for service in services:
        learning(service, args.dim, args.radius)
