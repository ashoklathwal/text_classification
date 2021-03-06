"""
tf-idf implementation:
    tfidf = log(tf + 1) * idf
    idf = log(N / df) (N: the number of documents, df: the number of documents containing the term)
"""

from collections import defaultdict
import math
from scipy.sparse import csr_matrix

from utils.util import *

__author__ = 'kensk8er'

from sklearn.datasets import load_svmlight_file

if __name__ == '__main__':

    threshold = 10

    # load the data
    print 'load train data...'
    X_train, Y_train = load_svmlight_file("data/train.csv", multilabel=True)
    print 'load test data...'
    X_test, Y_test = load_svmlight_file("data/test.csv", multilabel=True)

    N = X_train.get_shape()[0] + X_test.get_shape()[0]
    df = defaultdict(int)

    # count df for train data
    train_len = X_train.get_shape()[0]
    progress = 0
    print 'count df for train data...'
    for i in xrange(train_len):
        # print progress
        if (float(i) / train_len) * 100 > progress:
            print '\r', progress, '%',
            progress += 1

        row = X_train.getrow(i)
        for term in row.indices:
            df[term] += 1
    print '\r100 % done!'

    # count df for test data
    test_len = X_test.get_shape()[0]
    progress = 0
    print 'count df for test data...'
    for i in xrange(test_len):
        # print progress
        if (float(i) / test_len) * 100 > progress:
            print '\r', progress, '%',
            progress += 1

        row = X_test.getrow(i)
        for term in row.indices:
            df[term] += 1
    print '\r100 % done!'

    print 'save df...'
    enpickle(df, 'data/df.pkl')

    # calculate tfidf and update value for train data
    base = 2  # base for log function
    progress = 0
    index = 0  # index of the sparse matrix to which update value
    print 'calculate tf-idf and update value for train data...'
    train_mean = X_train.data.mean()
    for i in xrange(train_len):
        # print progress
        if (float(i) / train_len) * 100 > progress:
            print '\r', progress, '%',
            progress += 1

        row = X_train.getrow(i)
        for j in xrange(row.indices.size):
            term = row.indices[j]
            tf = row.data[j]
            idf = math.log(float(N) / df[term], base)
            tfidf = math.log(tf + 1, base) * idf

            X_train.data[index] = tfidf if tfidf > threshold else 0
            index += 1

    X_train.eliminate_zeros()
    print '\r100 % done!'

    # calculate tfidf and update value for test data
    progress = 0
    index = 0  # index of the sparse matrix to which update value
    print 'calculate tf-idf and update value for test data...'
    for i in xrange(test_len):
        # print progress
        if (float(i) / test_len) * 100 > progress:
            print '\r', progress, '%',
            progress += 1

        row = X_test.getrow(i)
        for j in xrange(row.indices.size):
            term = row.indices[j]
            tf = row.data[j]
            idf = math.log(float(N) / df[term], base)
            tfidf = math.log(tf + 1, base) * idf

            X_test.data[index] = tfidf if tfidf > threshold else 0
            index += 1
    X_test.eliminate_zeros()
    print '\r100 % done!'

    print 'reshape the matrix...'
    feature_len = max(X_train.shape[1], X_test.shape[1])
    X_train = csr_matrix((X_train.data, X_train.indices, X_train.indptr), shape=(train_len ,feature_len))
    X_test = csr_matrix((X_test.data, X_test.indices, X_test.indptr), shape=(test_len, feature_len))

    print 'saving train data...'
    enpickle(X_train, 'data/train_tfidf_sparse.pkl')
    print 'done!'

    print 'saving test data...'
    enpickle(X_test, 'data/test_tfidf_sparse.pkl')
    print 'done!'
