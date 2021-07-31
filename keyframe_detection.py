import click
import os
from natsort import os_sorted
import cv2
import pandas as pd
from tqdm import tqdm
from shot_detection import ShotDetection
from migrate import MySQLConnection

@click.command()
@click.option('--input', default='./videos/00492.mp4', required=True, show_default=True,
    help='Path to video. If not set to file, all videos in the path will be used.')
@click.option('--host', default='127.0.0.1', help='MySQL server hostname.')
@click.option('--port', default=3306, help='MySQL server port.')
@click.option('--user', default='', help='MySQL server user.')
@click.option('--password', default='', help='MySQL server password.')

def hello(input, host, port, user, password):
    """Find keyframes in a video, do object detection, and save results in a MySQL database."""
    
    click.echo(input)
    
    parse_input(input)


def parse_input(path):
    """If path does not point to a file, I will parse every video in the path"""

    input_path = r'/Users/bhuwan/Downloads/videos'
    output_path = r'/Users/bhuwan/Downloads/videos/output'
    video_extensions = ("mp4", "mkv", "flv", "wmv", "avi", "mpg", "mpeg")

    with MySQLConnection() as mysql:
        conn = mysql.connection
        if not input_path.endswith(video_extensions):
            for file in os_sorted(os.listdir(input_path)):
                if file.endswith(video_extensions):
                    video_path = input_path + '/' + file
                    print('Extracting frames from ' + video_path)
                    df = extract_frames(file, video_path)
                    sd = ShotDetection(df, output_path)
                    keyframes_df = sd.get_keyframes()
                    
                    tuples = list(keyframes_df.itertuples(index=False, name=None))
                    query = "INSERT INTO keyframes (video_id, video_path, keyframe_id, keyframe_path, shot, concept, confidence) \
                        VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    val = tuples
                    mysql.cursor.executemany(query, val)
                    mysql.connection.commit()
                    return

def extract_frames(video_id, video_path) -> pd.DataFrame:
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
    hello()