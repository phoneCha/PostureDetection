import cv2
import math as m
import mediapipe as mp
import time
import os
import csv
from datetime import datetime


class AngleCalculator:
    @staticmethod
    def find_angle(x1, y1, x2, y2, x3, y3):
        try:
            angle = m.degrees(m.atan2(y3 - y2, x3 - x2) - m.atan2(y1 - y2, x1 - x2))
            angle = abs(angle)
            if angle > 180:
                angle = 360 - angle
            return angle
        except ZeroDivisionError:
            return 0

    @staticmethod
    def get_angle_range(angle):
        start = (int(angle) // 10) * 10
        end = start + 10
        return f"{start}-{end}"


class CSVLogger:
    def __init__(self, output_dir, filename="hip_angle_log.csv"):
        self.csv_file = os.path.join(output_dir, filename)
        self.csv_header = ["Timestamp", "Image", "Side", "Hip Angle", "Angle Range", "Frequency", "Total Duration (s)"]
        self._initialize_csv()

    def _initialize_csv(self):
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(self.csv_header)

    def log_data(self, row):
        with open(self.csv_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(row)

    def update_data(self, rows):
        with open(self.csv_file, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(rows)

    def read_data(self):
        with open(self.csv_file, "r") as file:
            return list(csv.reader(file))


class PostureDetector:
    def __init__(self, snapshot_interval=10, output_dir="snapshots"):
        self.snapshot_interval = snapshot_interval
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.last_snapshot_time = time.time()
        self.log_tracker = {"left": {"range": None, "row": None}, "right": {"range": None, "row": None}}
        self.logger = CSVLogger(self.output_dir)
        self.pose = mp.solutions.pose.Pose()
        self.cap = cv2.VideoCapture(1)  # Change to 0 if camera 1 is not available

    def process_frame(self, frame):
        height, width = frame.shape[:2]
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.pose.process(frame_rgb)
        frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        if result.pose_landmarks:
            landmarks = result.pose_landmarks.landmark
            lmPose = mp.solutions.pose.PoseLandmark

            # Detect side facing camera
            left_shoulder_z = landmarks[lmPose.LEFT_SHOULDER].z
            right_shoulder_z = landmarks[lmPose.RIGHT_SHOULDER].z
            side_to_track = "left" if left_shoulder_z < right_shoulder_z else "right"

            # Get coordinates
            s = landmarks[lmPose.LEFT_SHOULDER] if side_to_track == "left" else landmarks[lmPose.RIGHT_SHOULDER]
            h_ = landmarks[lmPose.LEFT_HIP] if side_to_track == "left" else landmarks[lmPose.RIGHT_HIP]
            k = landmarks[lmPose.LEFT_KNEE] if side_to_track == "left" else landmarks[lmPose.RIGHT_KNEE]

            sx, sy = int(s.x * width), int(s.y * height)
            hx, hy = int(h_.x * width), int(h_.y * height)
            kx, ky = int(k.x * width), int(k.y * height)

            # Calculate angle
            angle = AngleCalculator.find_angle(sx, sy, hx, hy, kx, ky)
            angle_range = AngleCalculator.get_angle_range(angle)

            # Draw keypoints and lines
            cv2.circle(frame, (sx, sy), 7, (0, 255, 255), -1)
            cv2.circle(frame, (hx, hy), 7, (0, 255, 255), -1)
            cv2.circle(frame, (kx, ky), 7, (0, 255, 255), -1)
            cv2.line(frame, (sx, sy), (hx, hy), (255, 0, 0), 2)
            cv2.line(frame, (hx, hy), (kx, ky), (255, 0, 0), 2)

            # Display angle
            cv2.putText(frame, f'{side_to_track.capitalize()} Hip: {int(angle)} deg',
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Log data
            self.log_angle_data(side_to_track, angle, angle_range, frame)

        return frame

    def log_angle_data(self, side_to_track, angle, angle_range, frame):
        current_time = time.time()
        if current_time - self.last_snapshot_time >= self.snapshot_interval:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            image_name = f"{timestamp}_{side_to_track}.jpg"
            image_path = os.path.join(self.output_dir, image_name)
            cv2.imwrite(image_path, frame)

            if angle_range == self.log_tracker[side_to_track]["range"] and self.log_tracker[side_to_track]["row"]:
                # Update frequency and duration
                self.log_tracker[side_to_track]["row"][5] += 1
                self.log_tracker[side_to_track]["row"][6] += self.snapshot_interval

                rows = self.logger.read_data()
                for i in range(len(rows) - 1, 0, -1):
                    if rows[i][2] == side_to_track and rows[i][0] == self.log_tracker[side_to_track]["row"][0]:
                        rows[i] = [
                            self.log_tracker[side_to_track]["row"][0],
                            self.log_tracker[side_to_track]["row"][1],
                            self.log_tracker[side_to_track]["row"][2],
                            str(self.log_tracker[side_to_track]["row"][3]),
                            self.log_tracker[side_to_track]["row"][4],
                            str(self.log_tracker[side_to_track]["row"][5]),
                            str(self.log_tracker[side_to_track]["row"][6])
                        ]
                        break
                self.logger.update_data(rows)
            else:
                # New log entry
                new_row = [
                    timestamp, image_name, side_to_track,
                    int(angle), angle_range,
                    1, self.snapshot_interval
                ]
                self.log_tracker[side_to_track]["row"] = new_row
                self.log_tracker[side_to_track]["range"] = angle_range
                self.logger.log_data(new_row)

            self.last_snapshot_time = current_time

    def run(self):
        while True:
            success, frame = self.cap.read()
            if not success:
                print("No frame from camera.")
                break

            frame = self.process_frame(frame)
            cv2.imshow('Posture Detection', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    detector = PostureDetector()
    detector.run()
