import torch

from torch.utils.data import DataLoader
from torch.autograd import Variable
import pandas as pd
import nltk
from nltk.corpus import stopwords
import seaborn as sns
from sklearn import decomposition
import warnings
import matplotlib.pyplot as plt

# import learning.clustering
# import clustering


def show_picture(W1, vocabulary, labels):
    svd = decomposition.TruncatedSVD(n_components=2)
    W1_dec = svd.fit_transform(W1)

    x = W1_dec[:, 0]
    y = W1_dec[:, 1]
    plot = sns.scatterplot(x, y, hue = labels)

    for i in range(0, W1_dec.shape[0]):
        plot.text(x[i], y[i] + 2e-2, list(vocabulary.keys())[i], horizontalalignment='center', size='small',
                  color='black', weight='semibold')
    plt.show()


def get_input_tensor(tensor, vocab_size):
    size = [*tensor.shape][0]
    inp = torch.zeros(size, vocab_size).scatter_(1, tensor.unsqueeze(1), 1.)
    return Variable(inp).float()


def preprocess(corpus, stop_words):
    result = []
    for i in corpus:
        out = i.split()
        out = [x.lower() for x in out]
        out = [x for x in out if x not in stop_words]
        result.append(" ".join(out))
    return result


def create_vocabulary(corpus):
    vocabulary = {}

    i = 0

    for s in corpus:
        for w in s.split():
            if w not in vocabulary:
                vocabulary[w] = i
                i += 1
    return vocabulary


def prepare_set(corpus, n_gram=1):
    columns = ['Input'] + [f'Output{i + 1}' for i in range(n_gram * 2)]  # table_head, the length is n_gram*2
    result = pd.DataFrame(columns=columns)

    for sentence in corpus:
        for i, w in enumerate(sentence.split()):  # i: index; w: word
            inp = [w]
            out = []
            for n in range(1, n_gram + 1):  # [1,2, ... n_gram]
                if (i - n) >= 0:  # index >= n, means we should look back
                    out.append(sentence.split()[i - n])
                else:
                    out.append("<padding>")

                if (i + n) < len(sentence.split()):
                    out.append(sentence.split()[i + n])
                else:
                    out.append("<padding>")

            row = pd.DataFrame([inp + out], columns=columns)
            result = result.append(row, ignore_index=True)
    return result


def prepare_set_ravel(corpus, n_gram=1):
    columns = ['Input', 'Output']
    result = pd.DataFrame(columns=columns)
    for sentence in corpus:
        for i, w in enumerate(sentence.split()):
            inp = w
            for n in range(1, n_gram + 1):
                if i >= n:
                    out = sentence.split()[i - n]
                    row = pd.DataFrame([[inp, out]], columns=columns)
                    result = result.append(row, ignore_index=True)
                if (i + n) < len(sentence.split()):
                    out = sentence.split()[i + n]
                    row = pd.DataFrame([[inp, out]], columns=columns)
                    result = result.append(row, ignore_index=True)
    return result


def main(corpus, embedding=5):
    warnings.filterwarnings("ignore")

    # Remove stop words in the corpus
    stop_words = [str(x) for x in range(0, 10000)]
    stop_words = set(stop_words)
    corpus = preprocess(corpus, stop_words)

    # Create a dictionary
    vocabulary = create_vocabulary(corpus)
    # print(vocabulary)

    # train_emb = prepare_set(corpus, n_gram=2)
    # print(train_emb.head())

    train_emb = prepare_set_ravel(corpus, n_gram=2)

    train_emb.Input = train_emb.Input.map(vocabulary)
    train_emb.Output = train_emb.Output.map(vocabulary)
    # print(train_emb)

    vocab_size = len(vocabulary)

    embedding_dims = embedding

    device = torch.device('cpu')

    initrange = 0.5 / embedding_dims

    W1 = Variable(torch.randn(vocab_size, embedding_dims, device=device).uniform_(-initrange, initrange).float(),
                  requires_grad=True)
    W2 = Variable(torch.randn(embedding_dims, vocab_size, device=device).uniform_(-initrange, initrange).float(),
                  requires_grad=True)

    # w1:[20,5];w2[5.20]
    # print(f'W1 shape is: {W1.shape}, W2 shape is: {W2.shape}')

    num_epochs = 2000
    learning_rate = 2e-1
    lr_decay = 0.99
    loss_hist = []

    print("Start Learning.")
    for epo in range(num_epochs):
        for x, y in zip(DataLoader(train_emb.Input.values, batch_size=train_emb.shape[0]),
                        DataLoader(train_emb.Output.values, batch_size=train_emb.shape[0])):
            input_tensor = get_input_tensor(x, vocab_size)

            h = input_tensor.mm(W1)
            y_pred = h.mm(W2)

            loss_f = torch.nn.CrossEntropyLoss()
            loss = loss_f(y_pred, y)
            loss.backward()

            with torch.no_grad():
                W1 -= learning_rate * W1.grad.data
                W2 -= learning_rate * W2.grad.data

                W1.grad.data.zero_()
                W2.grad.data.zero_()

        if epo % 10 == 0:
            learning_rate *= lr_decay

        loss_hist.append(loss)
        # if epo % 50 == 0:
        #     print(f'Epoch {epo}, loss = {loss}')

    print("End Learning")

    W1 = W1.detach().numpy()
    # print(type(W1))

    # show_picture(W1, vocabulary)
    return W1, vocabulary

    learning.clustering.train(W1, list(vocabulary.keys()))
    # with open("./w1", "a+") as f:
    #     for i in W1:
    #         f.write(str(i)+'\n')
    # W2 = W2.detach().numpy()

    svd = decomposition.TruncatedSVD(n_components=2)
    W1_dec = svd.fit_transform(W1)

    x = W1_dec[:, 0]
    y = W1_dec[:, 1]
    plot = sns.scatterplot(x, y)

    # for i in range(0, W1_dec.shape[0]):
    #     plot.text(x[i], y[i] + 2e-2, list(vocabulary.keys())[i], horizontalalignment='center', size='small',
    #               color='black', weight='semibold')
    plt.show()

    # W2_dec = svd.fit_transform(W2)
    # x1 = W2_dec[:, 0]
    # y1 = W2_dec[:, 1]
    # plot1 = sns.scatterplot(x1, y1)
    #
    # for i in range(0, W2_dec.shape[0]):
    #     plot1.text(x1[i], y1[i] + 1, list(vocabulary.keys())[i], horizontalalignment='center', size='small',
    #                color='black', weight='semibold')
    # plt.show()