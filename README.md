# recsyschallenge2018

This repository contains code used to generate results submitted for the [Spotify RecSys Challenge 2018](https://recsys-challenge.spotify.com) by Team2Step (Dennis Leszkowicz)

Python 3.6 is recommended, as the final code has not been tested in Python 2.7 Make sure to install needed dependencies in ```requirements.txt``` by running ```pip install -r pip-requirements.txt```

### About Million Playlist Dataset (MPD)
The dataset consists of 1 million user generated playlists and comes in .json slices.

## 1) Loading the MPD
1. Run the following command:
```
python mpd_reader.py --input <FOLDERPATH to MPD source>
```
The script reads and trim the MPD json source files, retaining ``` pid and track_uri ``` saving it to a .tsv file in my_data/ directory.

## 2) Preprocessing the MPD and challenge-set
1. Run the following command:
```
python data_preprocessing.py --input <FOLDERPATH to challenge-set>
```

## 3) Generating recommendations for the challenge-set
1. Run the following command:
```
python recSys_recommender.py --input ../my_data/mpd_ch.tsv --output ../results/my_results.csv --model annoy_als --recommend
```
saves a csv submission file to results/ directory

### License
Usage of the Million Playlist Dataset is subject to these 
[license terms](https://recsys-challenge.spotify.com/license)
