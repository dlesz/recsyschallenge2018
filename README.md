# recsyschallenge2018

This repository contains code used to generate results submitted for the [Spotify RecSys Challenge 2018](https://recsys-challenge.spotify.com)

### About Million Playlist Dataset (MPD)
The dataset consists of 1 million user generated playlists and comes in .json slices.

## 1) Loading the MPD
2. Run the following command:
```
python restructureData.py --input <FOLDERPATH to MPD source>
```
The script trims reads the MPD json source, retains ``` pid, track_uri ``` and saves it to a .tsv file in the working directory.

## 2) Trimming the MPD and loading the challenge-set

## 3) Generating recommendations for the challenge-set

### License
Usage of the Million Playlist Dataset is subject to these 
[license terms](https://recsys-challenge.spotify.com/license)
