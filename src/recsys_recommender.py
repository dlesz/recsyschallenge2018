"""
    This is a script to run Implicit on the Spotify Million Playlist Dataset (MPD).
    Takes the MPD as a training-set and the challenge-set as the test-set as one input-file.
"""

from __future__ import print_function

import argparse
import codecs
import logging
import time
import numpy
import pandas
import sys
from scipy.sparse import coo_matrix

from implicit.als import AlternatingLeastSquares
from implicit.approximate_als import (AnnoyAlternatingLeastSquares, FaissAlternatingLeastSquares,
                                      NMSLibAlternatingLeastSquares)
from implicit.bpr import BayesianPersonalizedRanking
from implicit.nearest_neighbours import (BM25Recommender, CosineRecommender,
                                         TFIDFRecommender, bm25_weight)


# maps command line model argument to class name
MODELS = {"als":  AlternatingLeastSquares,
          "nmslib_als": NMSLibAlternatingLeastSquares,
          "annoy_als": AnnoyAlternatingLeastSquares,
          "faiss_als": FaissAlternatingLeastSquares,
          "tfidf": TFIDFRecommender,
          "cosine": CosineRecommender,
          "bpr": BayesianPersonalizedRanking,
          "bm25": BM25Recommender}


def get_model(model_name):
    model_class = MODELS.get(model_name)
    if not model_class:
        raise ValueError("Unknown Model '%s'" % model_name)

    # some default params
    if issubclass(model_class, AlternatingLeastSquares):
        params = {'factors': 128, 'iterations': 15, 'dtype': numpy.float32, 'use_gpu': True, 'calculate_training_loss':True, 'use_cg':True, 'use_native':True}
    elif model_name == "bm25":
        params = {'K1': 100, 'B': 0.5}
    elif model_name == "bpr":
        params = {'factors': 63, 'use_gpu': False}
    else:
        params = {}

    return model_class(**params)


def read_data(filename):
    """ Reads in the MPD dataset, and returns a tuple of a pandas dataframe
    and a sparse matrix of artist/pid/track_count """

    # read in triples of pid/track_uri/track_count from the input dataset
    # creating a model based off the input params
    start = time.time()
    logging.debug("reading data from %s", filename)
    data = pandas.read_csv(filename, sep='\t', dtype={"pid": 'category', "track_uri": 'category', "track_count": int})

    # map each track_uri and pid to a unique numeric value
    data['track_uri'] = data['track_uri'].astype('category')
    data['pid'] = data['pid'].astype('category')
    data['track_count'] = data['track_count'].astype(int)

    # create a sparse matrix of all the pids/track_count
    matrix = coo_matrix((data['track_count'].astype(numpy.float32),
                       (data['track_uri'].cat.codes.copy(),
                        data['pid'].cat.codes.copy())))

    logging.debug("read data file in %s", time.time() - start)

    return data, matrix

def calculate_recommendations(input_filename, output_filename, model_name):
    """ Generates track_uri recommendations for each pid in the dataset """

    df, track_count = read_data(input_filename)

    # create a model from the input data
    model = get_model(model_name)

    # if we're training an ALS based model, weight input by bm25
    if issubclass(model.__class__, AlternatingLeastSquares):

        logging.debug("weighting matrix by bm25_weight")
        track_count = bm25_weight(track_count, K1=100, B=0.8)

        # disable building approximate recommend index
        model.approximate_similar_items = False

    # transpose the training_matrix
    track_count = track_count.tocsr()

    logging.debug("training model %s", model_name)
    start = time.time()
    model.fit(track_count)
    logging.debug("trained model '%s' in %0.2fs", model_name, time.time() - start)

    # generate recommendations for each pid and creating submission file

    first_line = 'team_info,team_name,main,your@email.com'
    recs = ['']

    tracks = dict(enumerate(df['track_uri'].cat.categories))
    start = time.time()
    pid_track_counts = track_count.T.tocsr()

    with codecs.open(output_filename, "w") as o:
        o.write("%s \n" %(first_line))
        o.write("\n")
        for playlist_id, pid in enumerate(df['pid'].cat.categories):

            for track_id, score in model.recommend(playlist_id, pid_track_counts, N=500):
                    recs.append(tracks[track_id])

            if int(pid)>=1000000:
                o.write("%s" %(pid))
                recs = ','.join(map(str, recs))
                o.write(recs)
                o.write("\n")
                o.write("\n")

            recs = ['']
    logging.debug("generated recommendations in %0.2fs",  time.time() - start)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Generates recommendations for each pid in the challenge-set",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--input', type=str,
                        dest='inputfile', help='Spotify mpd data file', required=True)
    parser.add_argument('--output', type=str, required=True,
                        dest='outputfile', help='output file name')
    parser.add_argument('--model', type=str, default='als',
                        dest='model', help='model to calculate (%s)' % "/".join(MODELS.keys()))
    parser.add_argument('--recommend',
                        help='Recommends items for each pid in the challenge-set',
                        action="store_true")
    parser.add_argument('--param', action='append',
                        help="Parameters to pass to the model, formatted as 'KEY=VALUE")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    if args.recommend:
        calculate_recommendations(args.inputfile, args.outputfile, model_name=args.model)
    else:
        calculate_similar_artists(args.inputfile, args.outputfile, model_name=args.model)
