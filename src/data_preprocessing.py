import pandas as pd
import numpy
import time
import argparse
import logging
import numpy as np
import os, json
from scipy.sparse import coo_matrix
from pandas.io.json import json_normalize

def read_challenge(folderpath):
    start = time.time()
    logging.debug("reading challenge-set from %s", folderpath)

    ch_df = pd.read_json(folderpath+'/challenge_set.json')

    tracks_ch = json_normalize(ch_df['playlists'], record_path='tracks',
                            meta=['pid','num_samples'], errors='ignore')

    # trimming df
    tracks_ch = tracks_ch[['pid','track_uri']]

    challenge_df = tracks_ch.copy()

    final_ch_df = sampling_missing_seeds(ch_df, challenge_df, tracks_ch)

    # preferred order: pid, track_uri, track_count
    final_ch_df = final_ch_df.reindex(columns=['pid', 'track_uri', 'track_count'])

    final_ch_df['track_count']=1

    logging.debug("read challenge-set file in %s", time.time() - start)
    return final_ch_df

def sampling_missing_seeds(ch_df, challenge_df, tracks_ch):
# Sampling random tracks for playlists with missing seeds.
# This approach is very naive and does not produce consistent results.
# However, it works as a baseline for now.

    # iterating over the challenge-set
    count = 0
    for i, r in ch_df.iterrows():
        if(ch_df['playlists'][i]['num_samples']==0):
            count +=1
            try:
                # sampling n tracks from challenge-set seeds, adding pid and appending to final challenge_df
                n = 10
                sample_instance = tracks_ch.track_uri.sample(n)
                samples_df = pd.DataFrame(sample_instance)
                samples_df['pid']=ch_df['playlists'][i]['pid']
                challenge_df = challenge_df.append(samples_df, sort=False) # sort = False To retain the current behavior and silence the warning
            except:
                pass
    #print('# of pids with zero samples: ' + str(count))
    return challenge_df

def read_trim_mpd():
    '''reading mpd and reducing noise in the mpd.'''
    start = time.time()

    logging.debug("reading mpd")
    # reading trimmed mpd from my_data/
    mpd_df = pd.read_csv('../my_data/mpd.tsv', sep='\t')
    logging.debug("read mpd file in %s", time.time() - start)

    start = time.time()
    logging.debug("removing noise from the dataset")

    mpd_df['track_count']=1

    # making a copy of the mpd to be used for counting song appearance across the mpd
    mpd_count = mpd_df.copy()

    # Summing duplicate tracks rows
    mpd_count = mpd_count.groupby(['track_uri'])['track_count'].sum().reset_index()

    # removing noise by keeping only songs that appear more than 177 times in the mpd
    mpd_filtered = mpd_count[mpd_count['track_count']> 177]

    # merging the mpd_df with mpd_filtered by the intersection, creating a new df
    mpd_output_df = pd.merge(mpd_df, mpd_filtered, how='inner', on=['track_uri'])

    # renaming column
    mpd_output_df.rename(columns={"track_count_x": "track_count"},inplace=True)

    # reordering columns
    mpd_output_df = mpd_output_df[['pid','track_uri','track_count']]

    logging.debug("trimmed mpd file in %s", time.time() - start)

    return mpd_output_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reads the trimmed MPD in my_data/, reads the challenge_set from args --input (folderpath) and then preprocesses the data.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--input', type=str,
                        dest='folderpath', help='specify path to challenge_set', required=True)

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    challenge_df = read_challenge(args.folderpath)
    mpd = read_trim_mpd()

    start = time.time()
    logging.debug("merging mpd and challenge-set")
    # finally, merge your mpd and challenge_set
    final_mpd = mpd.append(challenge_df)
    logging.debug("merged mpd and challenge-set in %s", time.time() - start)

    start = time.time()
    logging.debug("writing dataset to file")
    final_mpd.to_csv('../my_data/mpd_ch.tsv', sep='\t', index=False)
    logging.debug("wrote dataset to file in %s", time.time() - start)

    #logging.debug("reading challenge-set from %s", folderpath)
    #logging.debug("read challenge-set file in %s", time.time() - start)
