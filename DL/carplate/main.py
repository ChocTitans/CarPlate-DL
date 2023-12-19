
import sys
sys.path.append("..")  # Adjust the path to include the parent directory
import os
import cv2
import numpy as np
from ultralytics import YOLO
import subprocess
import time
from sort.sort import Sort
from util import get_car, read_license_plate, write_csv
from DL.config import app
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)


from app import save_license_plate, update_progress, reset_progress


if __name__ == '__main__':
    if len(sys.argv) > 1:
        video_filename = sys.argv[1]  # Get the video filename from command line argument
        user_id = sys.argv[2]  # Get user ID from command line argument

        # Construct the video file path using the received filename
        video_path = f'./uploads/{video_filename}'
        cap = cv2.VideoCapture(video_path)

        results = {}
        mot_tracker = Sort()

        # load models
        coco_model = YOLO('./carplate/yolov8n.pt')
        license_plate_detector = YOLO('./carplate/best.pt')

        vehicles = [2, 3, 5, 7]

        total_frames = 50  # Assuming 10 frames as the limit
        frame_count = 0  # Initialize the frame counter
        current_progress = 0
        frame_nmr = -1
        ret = True
        while ret:
            frame_nmr += 1
            ret, frame = cap.read()
            if ret:
                if frame_count >= total_frames:  # Check frame_count instead of frame_nmr
                    break
                results[frame_nmr] = {}
                frame_count += 1
                current_progress = int((frame_count / total_frames) * 100)
                with app.app_context():  # Establish the app context
                    update_progress(current_progress)
                # detect vehicles
                detections = coco_model(frame)[0]
                detections_ = []
                for detection in detections.boxes.data.tolist():
                    x1, y1, x2, y2, score, class_id = detection
                    if int(class_id) in vehicles:
                        detections_.append([x1, y1, x2, y2, score])

                # track vehicles
                track_ids = mot_tracker.update(np.asarray(detections_))

                # detect license plates
                license_plates = license_plate_detector(frame)[0]
                for license_plate in license_plates.boxes.data.tolist():
                    x1, y1, x2, y2, score, class_id = license_plate

                    # assign license plate to car
                    xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)

                    if car_id != -1:
                        # crop license plate
                        license_plate_crop = frame[int(y1):int(y2), int(x1): int(x2), :]

                        # process license plate
                        license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
                        _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_gray, 79, 255, cv2.THRESH_BINARY_INV)

                        # read license plate number
                        license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop_thresh)
                        if license_plate_text is not None:
                            with app.app_context():  # Establish the app context
                                if license_plate_text_score >= 0.55:
                                    save_license_plate(license_plate_text, user_id)

                            results[frame_nmr][car_id] = {'car': {'bbox': [xcar1, ycar1, xcar2, ycar2]},
                                                          'license_plate': {'bbox': [x1, y1, x2, y2],
                                                                            'text': license_plate_text,
                                                                            'bbox_score': score,
                                                                            'text_score': license_plate_text_score}}
        # write results
        print("Writing in the csv")
        write_csv(results, './carplate/test.csv')
        time.sleep(3)
        print("Executing the add_missing_data scripts")
        subprocess.run(['python', './carplate/add_missing_data.py'])
        time.sleep(5)

        print("Executing the visualize scripts")
        # Execute the second script
        process = subprocess.Popen(['python', './carplate/visualize.py', video_filename])

        # Wait for the subprocess to complete
        process.wait()
        time.sleep(2)
        with app.app_context():
            current_progress = 100
            time.sleep(3)
            reset_progress()
    else:
        print("Please provide the video filename as a command line argument")
    