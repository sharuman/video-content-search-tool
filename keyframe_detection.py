import click
import os
from natsort import os_sorted
import cv2
import pandas as pd
from tqdm import tqdm
from shot_detection import ShotDetection
from database import MySQLConnection

@click.command()
@click.option('--input', default='./videos/00492.mp4', required=True, show_default=True,
    help='Path to video. If not set to file, all videos in the path will be used.')
@click.option('--host', default='127.0.0.1', help='MySQL server hostname.')
@click.option('--port', default=3306, help='MySQL server port.')
@click.option('--user', default='', help='MySQL server user.')
@click.option('--password', default='', help='MySQL server password.')
@click.option('--reset/--no-reset', default=False)

def parse_input(input, host, port, user, password, reset):
    """Find keyframes in a video, do object detection, and save results in a MySQL database.
    
    If path does not point to a file, I will parse every video in the path
    """
    
    output_path = r'static/keyframes'
    video_extensions = ("mp4", "mkv", "flv", "wmv", "avi", "mpg", "mpeg")

    with MySQLConnection(reset) as mysql:
        conn = mysql.connection
        if not input.endswith(video_extensions):
            for file in os_sorted(os.listdir(input)):
                if file.endswith(video_extensions):
                    video_path = input + '/' + file
                    print('Extracting frames from ' + video_path)
                    df = extract_frames(file, video_path)
                    sd = ShotDetection(df, output_path)
                    keyframes_df = sd.get_keyframes()
                    
                    tuples = list(keyframes_df.itertuples(index=False, name=None))
                    query = "INSERT INTO keyframes (video_id, video_path, keyframe_id, keyframe_path, shot, concept, confidence) \
                        VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    mysql.cursor.executemany(query, tuples)
                    mysql.connection.commit()

def extract_frames(video_id, video_path) -> pd.DataFrame:
    """Frames of the input video are extracted using openCV library.

    Args:
        video_id (string):  file name of the video.
        video_path (string): path to the video.
    Returns:
        pd.DataFrame:  a dataframe having all the relevant information of the video.
    """

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    tot_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    print('FPS (Frames Per Second): ' + str(fps))
    print('Number of frames in the video: ' + str(tot_frames))
    print('Extracting frames')

    data = []

    #Extracting and saving video frames in memory
    i=0
    with tqdm(total=tot_frames) as pbar:
        while(cap.isOpened()):
            res, frame = cap.read()
            if res == False:
                break
            data.append((video_id, video_path, i, frame))
            pbar.update(1)
            i+=1
    
    df = pd.DataFrame(data, columns = ['video_id', 'video_path', 'frame_id', 'frame'])

    cap.release()
    cv2.destroyAllWindows()

    return df

if __name__ == '__main__':
    parse_input()