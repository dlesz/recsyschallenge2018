from __future__ import print_function

import argparse
import codecs
import logging
import time
import numpy
import pandas as pd
from pandas.io.json import json_normalize
import os
import json

def read_data(folderpath):

    start = time.time()
    logging.debug("reading data from %s", folderpath)

    # creating empty df
    tracks_df = pd.DataFrame(columns=['pid','track_uri'])

    path_to_json = folderpath
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

    json_files.sort()

    # we need both the json and an index number so use enumerate()
    for index, js in enumerate(json_files):
        s = time.time()
        with open(os.path.join(path_to_json, js)) as json_file:
            j = json.load(json_file)

            # extracting tracks from playlists in each slice
            tracks = json_normalize(j['playlists'], record_path='tracks',
                                meta=['pid'])

            # append tracks to tracks_df
            tracks = tracks[['pid', 'track_uri']]
            tracks_df = tracks_df.append(tracks)
        #print('reading slice #'+ str(index) + ' in : '+ str(s-time.time()))
    logging.debug("read data file in %s", time.time() - start)

    start = time.time()
    logging.debug("writing data to file")
    tracks_df.to_csv('../my_data/mpd.tsv', sep='\t', index=False)
    logging.debug("wrote data file in %s", time.time() - start)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reads the MPD, trims and saves it to a .tsv file",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--input', type=str,
                        dest='folderpath', help='specify path to folder with spotify-mpd json slices', required=True)

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    read_data(args.folderpath)
