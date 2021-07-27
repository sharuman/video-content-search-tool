# Video Search
The following setup has been tested on MBP running macOS Catalina.

## Conda environment
1. conda env create -f environment.yml
2. conda activate video-search-python


## Database setup
0. Install brew
1. `brew install mysql`
2. `mysql.server start`
3. `/opt/anaconda3/envs/video-search-python/bin/python path-to/migrate.py`
4. `/opt/anaconda3/envs/video-search-python/bin/python path-to/app.py`
