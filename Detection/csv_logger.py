import os
import csv

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
