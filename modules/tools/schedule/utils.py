import csv
import json
from datetime import datetime, timedelta
import pandas as pd

class TKB:
    def __init__(self, csv_file):
        self.csv_file = csv_file

    def read_csv(self):
        self.data = pd.read_csv(self.csv_file)

        # Fill NaN values with the value above or "" if no value exists above
        self.data.fillna(method='ffill', inplace=True)
        self.data.fillna("", inplace=True)

    def generate_schedule(self):
        self.read_csv()
        schedule = {}

        def generate_dates(start_date, end_date):
            current_date = start_date
            while current_date <= end_date:
                yield current_date
                current_date += timedelta(days=1)

        def expand_periods(period_range):
            start, end = map(int, period_range.split("-"))
            return list(range(start, end + 1))

        for _, row in self.data.iterrows():
            class_id = row["Tên lớp tín chỉ"]
            if class_id not in schedule:
                schedule[class_id] = {
                    "Số tín chỉ": row["Số tín chỉ"],
                    "Tên học phần": row["Tên học phần"],
                    "Thời gian - Tiết": {},
                    "Giáo viên": [],
                    "Phòng": []
                }

            # Process "Thời gian - Tiết"
            if row["Thời gian"] and row["Thứ"] and row["Tiết"]:
                start_date_str, end_date_str = row["Thời gian"].split("-")
                start_date = datetime.strptime(start_date_str.strip(), "%d/%m/%Y")
                end_date = datetime.strptime(end_date_str.strip(), "%d/%m/%Y")
                day_of_week = int(row["Thứ"]) - 2  # Convert to Python's weekday format (Mon=0, Sun=6)
                periods = expand_periods(row["Tiết"])

                for date in generate_dates(start_date, end_date):
                    if date.weekday() == day_of_week:
                        date_str = date.strftime("%d/%m/%Y")
                        if date_str not in schedule[class_id]["Thời gian - Tiết"]:
                            schedule[class_id]["Thời gian - Tiết"][date_str] = []
                        schedule[class_id]["Thời gian - Tiết"][date_str].extend(periods)

            # Add "Giáo viên"
            if row["Giáo viên"] and row["Giáo viên"] not in schedule[class_id]["Giáo viên"]:
                schedule[class_id]["Giáo viên"].append(row["Giáo viên"])

            # Add "Phòng"
            if row["Phòng"] and row["Phòng"] not in schedule[class_id]["Phòng"]:
                schedule[class_id]["Phòng"].append(row["Phòng"])

        return schedule

    def save_to_json(self, json_file):
        schedule = self.generate_schedule()
        with open(json_file, mode="w", encoding="utf-8") as file:
            json.dump(schedule, file, ensure_ascii=False, indent=4)

    def get_dict(self):
        """Returns the processed data as a dictionary."""
        return self.generate_schedule()
    
    def find_item_by_date(self, date_str):
        """Finds items in the schedule that have the given date."""
        schedule = self.get_dict()
        result = {}

        for class_id, details in schedule.items():
            if date_str in details["Thời gian - Tiết"]:
                result[class_id] = {
                    "Số tín chỉ": details["Số tín chỉ"],
                    "Tên học phần": details["Tên học phần"],
                    "Giáo viên": details["Giáo viên"],
                    "Phòng": details["Phòng"],
                    "Tiết": details["Thời gian - Tiết"][date_str]
                }

        return result

if __name__ == "__main__":
    # Usage Example
    csv_file = "./students/2055010051.csv"
    tkb = TKB(csv_file)

    # Get dictionary
    schedule_dict = tkb.get_dict()
    print(schedule_dict)

    # Save to JSON
    json_file = "output.json"
    tkb.save_to_json(json_file)

    date_to_search = "25/09/2024"
    results = tkb.find_item_by_date(date_to_search)
    print(results)
