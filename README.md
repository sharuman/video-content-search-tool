# Video Content Search Tool
This project let you search concepts in a video via a web interface. If first detects the shots by using the Twin Comparison Algorithm. Then, the frame in the middle of each shot is choosen as keyframe. Afterwards, each keyframe is feeded to the VGG16 CNN to extract the concepts (for each keyframe we extract the concept with the highest confidence). In the end, the resutls are persisted in a MySQL database so that they can be browsed by the user using the web-based UI.

## Setup
The following setup has been tested on MBP running macOS Catalina using the V3C1 dataset.
### Conda environment
1. `conda env create -f environment.yml`
2. `conda activate video-search-python`

To update the environment use `conda env update -f environment.yml --prune`.

### Database
0. Install brew
1. `brew install mysql`
2. `mysql.server start`
3. `cp .env.example .env`.
4. Set the `.env` file accordingly.
5. `python keyframe_detection.py --input='path-to-videos'`
6. `python app.py`
