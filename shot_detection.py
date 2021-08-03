import cv2
import numpy as np
import pandas as pd
from scipy.spatial import distance
import math
import os
from tensorflow.keras.preprocessing import image as kerasImage
import tensorflow.keras.applications.vgg16 as vgg16
from PIL import Image

class ShotDetection():
    """Shot Boundary Detection using Twin-comparison Algorithm."""

    def __init__(self, images_dataframe, output_path):
        """Creates an objet to do shot detection in a video.
        
        Twin Comparison Algorithm is used for shot detection.
        """
        
        self.__images_dataframe = images_dataframe
        self.__output_path = output_path
        
    def __get_histograms(self):
        """Return histogrames of the compressed images.

        The RGB images (frames) are compressed by reserving:
        - 3 bits for the Red channel;
        - 3 bits for the Green channel;
        - 2 bits for the Blue channel.

        Returns:
            list:  a list of histograms for each frame present in the dataframe.
        """

        histograms = []

        for index, row in self.__images_dataframe.iterrows():
            image = row['frame']
            channels = cv2.split(image)
            B = channels[0].reshape(-1)
            G = channels[1].reshape(-1)
            R = channels[2].reshape(-1)
            R = R >> 5
            G = G >> 5
            B = B >> 6
            
            R = R << 5
            G = G << 2
            compressedImage = np.add(R, G, B)
            # At this point we only need to focus on one channel as we
            # have converted 'compressedImage' to 1-d array.
            hist = cv2.calcHist([compressedImage], [0], None, [64], [0, 255])
            histograms.append(hist)
            
        return histograms

    def __twin_comparison(self, framesHistogram, thresholdHigh, thresholdLow) -> list:
        """Twin Comparison Algorithm implementation that aims to detect shots boundary in a video.

        Args:
            framesHistogram (list):  a list of histograms for all the frames in the input video.
            thresholdHigh (float):  higher threshold dynamically calulated for each video.
            thresholdLow (float):  lower threshold dynamically calulated for each video.

        Returns:
            list:  a list containing the shots boundary where each element is a tuple
            (start_boundary_frame_id, end_boundary_frame_id).
        """

        shots = []
        count_shots = 1
        
        i = 0 # shot start
        j = 0 # shot end
        accumDiff = 0
        for frame in framesHistogram:
            # represent a single pin in our twin-comparison method histogram
            if(j < len(framesHistogram) - 1):
                frames_distance = distance.cityblock(framesHistogram[j], framesHistogram[j+1])

                if(thresholdLow < frames_distance < thresholdHigh):
                    difference = frames_distance - thresholdLow
                    
                    accumDiff += difference
                    if(accumDiff > thresholdHigh):
                        shots.append((i, j))
                        j += 1
                        i = j
                        accumDiff = 0
                        count_shots+=1

                # easy way out
                if(frames_distance > thresholdHigh):
                    shots.append((i, j))
                    j += 1
                    i = j
                    accumDiff = 0
                    count_shots+=1
                
                j += 1
                
        return shots

    def __getHigherThreshold(self, diff_list) -> float:
        """Generate the higher threshold to be used in the Twin-comparison Algorithm.

        After identifying the peak value, we assign higher_thresh the index value that
        corresponds to half of the peak value on the right slope of the peak.
        higher_thresh must be higher than mean value.

        Args:
            diff_list (list):  a list having the distance between consecutive histograms.

        Returns:
            float:  higher threshold.
        """

        higherThresh_calc = np.max(diff_list)/2

        if higherThresh_calc > np.average(diff_list):
            print("Higher threshold: ", higherThresh_calc)

            return higherThresh_calc
        
    def __getLowerThreshold(self, diff_list) -> float:
        """Generate the lower threshold to be used in the Twin-comparison Algorithm.

        The lower threshold can be calculated using equation:
                lower_thresh = mi + alpha*sigma
        where mi and sigma are the mean and standard deviations of interframe differences.
        The alpha is constant (5 is the suggested value).

        Args:
            diff_list (list):  a list having the distance between consecutive histograms.

        Returns:
            float:  lower threshold.
        """

        lowerThresh_calc = np.average(diff_list) + 2*(np.std(diff_list))
        print("Lower threshold: ", lowerThresh_calc)

        return lowerThresh_calc
 
    def __getThresholds(self, hist_list) -> tuple:
        """Computation of the higher and lower thresholds.

        Args:
            hist_list (list):  a list of histograms for each frame present in the input video.

        Returns:
            tuple:  higher and lower thresholds.
        """

        frames_distances = []
        
        for i in range(len(hist_list)):
            # represent a single pin in our twin-comparison method histogram
            if(i < len(hist_list) - 1):
                frames_distances.append(distance.cityblock(hist_list[i], hist_list[i+1]))

        return (self.__getHigherThreshold(frames_distances), self.__getLowerThreshold(frames_distances))


    def get_keyframes(self) -> pd.DataFrame:
        """Extract the keyframe from each shot boundary.

        The keyframe is simply the middle frame in the shot boundary.

        Args:
            shots (list):  a list containing the shots boundary where each element is a tuple
            (start_boundary_frame_id, end_boundary_frame_id).
        Returns:
            list:  a list of keyframes (images) as numpy arrays.
        """

        histograms = self.__get_histograms()
        thresholdHigh, thresholdLow = self.__getThresholds(histograms)
        shots = self.__twin_comparison(histograms, thresholdHigh, thresholdLow)

        os.makedirs(os.path.dirname(self.__output_path + '/'), exist_ok=True)
        # file1 = open(self.__output_path + '/shots.txt', 'w') 

        shot = 0
        keyframes = []
        for start_frame, end_frame in shots:
            # file1.write(str(start_frame) + '-' + str(end_frame) + ' (Shot ' + str(shot) + ')\n')

            mid_point = math.floor((start_frame + end_frame) / 2)
            row = self.__images_dataframe.iloc[mid_point]

            keyframe = row['frame']
            
            keyframe_path = self.__output_path + '/' + row['video_id'] + '-keyframe-' + str(mid_point) + '-shot-' + str(shot) + '.jpg'
            cv2.imwrite(keyframe_path, keyframe)

            concept, confidence = self.__funcVGG16(keyframe)

            keyframes.append((row['video_id'], row['video_path'], row['frame_id'], keyframe_path, shot, concept, confidence))

            shot+=1

        # file1.close()
        
        df = pd.DataFrame(keyframes, columns = ['video_id', 'video_path', 'keyframe_id', 'keyframe_path', 'shot', 'concept', 'confidence'])
        
        return df

    def __funcVGG16(self, img):
        """VGG16 Convolutional Neural Network for image recognition.

        Args:
            img (numpy array):  numpy array representing an image (in BGR) on
            which we want to do image recognition. 


        Returns:
            tuple:  tuple of label (concept) and probability (integer).
            The label with the highest probability is returned.
        """
        
        model = vgg16.VGG16(weights='imagenet')
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # LANCZOS is a high quality filter for both downscaling and upscaling images.
        # @see  https://pillow.readthedocs.io/en/stable/handbook/concepts.html#PIL.Image.LANCZOS
        img = Image.fromarray(img).resize((224, 224), Image.LANCZOS)
        x = kerasImage.img_to_array(img)

        x = np.expand_dims(x, axis=0)
        x = vgg16.preprocess_input(x)

        preds = model.predict(x)
        
        _, label, probability = vgg16.decode_predictions(preds, top=3)[0][0]
        
        return (label, round(probability, 2) * 100)