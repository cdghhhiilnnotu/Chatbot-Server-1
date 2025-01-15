import pandas as pd
import json
import csv
from datetime import datetime, timedelta

class MonHoc:
    def __init__(self, csv_file):
        # Read the CSV file
        self.csv_file = csv_file

    def read_data(self):
        self.data = pd.read_csv(self.csv_file)

        # Explicitly cast numeric columns to string if needed
        for col in self.data.select_dtypes(include=["float64", "int64"]).columns:
            self.data[col] = self.data[col].astype("object")

        # Fill NaN values with the value above or "" if no value exists above
        self.data.fillna(method='ffill', inplace=True)
        self.data.fillna("", inplace=True)


    def get_content(self):
        self.read_data()
        # Group by 'Tên lớp tín chỉ'
        summary = {}
        class_id = ""
        for _, row in self.data.iterrows():
            if row["Tên lớp tín chỉ"]:
                class_id = row["Tên lớp tín chỉ"]
            if class_id:
                if class_id not in summary:
                    summary[class_id] = {
                        "Số tín chỉ": row["Số tín chỉ"],
                        "Tên học phần": row["Tên học phần"],
                        "Thời gian": [],
                        "Thứ": [],
                        "Tiết": [],
                        "Giáo viên": set(),  # Use a set to avoid duplicate entries
                        "Số lượng": []
                    }
                summary[class_id]["Thời gian"].append(row["Thời gian"])
                summary[class_id]["Thứ"].append(row["Thứ"])
                summary[class_id]["Tiết"].append(row["Tiết"])
                summary[class_id]["Số lượng"].append(row["Số lượng"])
                if row["Giáo viên"]:
                    summary[class_id]["Giáo viên"].add(row["Giáo viên"])

        # Convert 'Giáo viên' back to a list for consistency
        for class_id in summary:
            summary[class_id]["Giáo viên"] = list(summary[class_id]["Giáo viên"])

        return summary
    
    def success_submit(self):
        header = ["STT", "Tên học phần", "Số tín chỉ", "Tên lớp tín chỉ", "Thời gian", "Thứ", "Tiết", "Số lượng", "Giáo viên"]
        data = self.get_content()
        # Write data to CSV
        with open(self.csv_file, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)

            stt = 1  # Initialize the STT counter
            for class_code, details in data.items():
                # Write the first row with full data
                writer.writerow([
                    stt,
                    details["Tên học phần"],
                    details["Số tín chỉ"],
                    class_code,
                    details["Thời gian"][0],
                    details["Thứ"][0],
                    details["Tiết"][0],
                    details["Số lượng"][0],
                    details["Giáo viên"][0]
                ])
                # Write subsequent rows for additional times with shared data as empty strings
                for i in range(1, len(details["Thời gian"])):
                    writer.writerow([
                        "",
                        "",
                        "",
                        "",
                        details["Thời gian"][i],
                        details["Thứ"][i],
                        details["Tiết"][i],
                        details["Số lượng"][i]-1,
                        ""
                    ])
                stt += 1

    def get_days(self):
        def generate_dates(start_date, end_date):
            current_date = start_date
            while current_date <= end_date:
                yield current_date
                current_date += timedelta(days=1)

        def expand_periods(period_range):
            start, end = map(int, period_range.split("-"))
            return list(range(start, end + 1))

        def get_days_with_periods(timelines, specific_days, lesson_periods):
            result = {}
            for timeline, day, period in zip(timelines, specific_days, lesson_periods):
                start_str, end_str = timeline.split("-")
                start_date = datetime.strptime(start_str, "%d/%m/%Y")
                end_date = datetime.strptime(end_str, "%d/%m/%Y")
                expanded_periods = expand_periods(period)

                for date in generate_dates(start_date, end_date):
                    if date.weekday() == day - 2:  # Match only the specific day of the week
                        date_str = date.strftime("%d/%m/%Y")
                        result[date_str] = expanded_periods

            return result

        content = self.get_content()
        time_summary = {}
        for class_id in content:
            if int(content[class_id]["Số lượng"][0]) > 1:
                time_summary[class_id] = get_days_with_periods(content[class_id]["Thời gian"],
                                                               content[class_id]["Thứ"],
                                                               content[class_id]["Tiết"])
        return time_summary

    # def save_json(self, output_file):
    #     time_summary = self.get_days()
    #     with open(output_file, "w", encoding="utf-8") as json_file:
    #         json.dump(time_summary, json_file, indent=4, ensure_ascii=False)
    #     print(f"JSON saved to {output_file}")

class TKB:
    def __init__(self, csv_file):
        # Read the CSV file
        self.csv_file = csv_file

    def read_data(self):
        self.data = pd.read_csv(self.csv_file)

        # Explicitly cast numeric columns to string if needed
        for col in self.data.select_dtypes(include=["float64", "int64"]).columns:
            self.data[col] = self.data[col].astype("object")

        # Fill NaN values with the value above or "" if no value exists above
        self.data.fillna(method='ffill', inplace=True)
        self.data.fillna("", inplace=True)


    def get_content(self):
        self.read_data()
        # Group by 'Tên lớp tín chỉ'
        summary = {}
        class_id = ""
        for _, row in self.data.iterrows():
            if row["Tên lớp tín chỉ"]:
                class_id = row["Tên lớp tín chỉ"]
            if class_id:
                if class_id not in summary:
                    summary[class_id] = {
                        "Số tín chỉ": row["Số tín chỉ"],
                        "Tên học phần": row["Tên học phần"],
                        "Thời gian": [],
                        "Thứ": [],
                        "Tiết": [],
                        "Giáo viên": set(),  # Use a set to avoid duplicate entries
                        "Phòng": []
                    }
                summary[class_id]["Thời gian"].append(row["Thời gian"])
                summary[class_id]["Thứ"].append(row["Thứ"])
                summary[class_id]["Tiết"].append(row["Tiết"])
                summary[class_id]["Phòng"].append(row["Phòng"])
                if row["Giáo viên"]:
                    summary[class_id]["Giáo viên"].add(row["Giáo viên"])

        # Convert 'Giáo viên' back to a list for consistency
        for class_id in summary:
            summary[class_id]["Giáo viên"] = list(summary[class_id]["Giáo viên"])

        return summary
    
    def delete_content(self, maTC):
        del_key = []
        tkb = self.get_content()
        for key, value in tkb.items():
            if key.split("_")[0] == maTC:
                del_key.append(key)
        for key in del_key:
            tkb.pop(key, None)
        self.update_content(tkb)

    def update_content(self, data):
        header = ["STT", "Tên học phần", "Số tín chỉ", "Tên lớp tín chỉ", "Thời gian", "Thứ", "Tiết", "Phòng", "Giáo viên"]

        # Write data to CSV
        with open(self.csv_file, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)

            stt = 1  # Initialize the STT counter
            for class_code, details in data.items():
                # Write the first row with full data
                writer.writerow([
                    stt,
                    details["Tên học phần"],
                    details["Số tín chỉ"],
                    class_code,
                    details["Thời gian"][0],
                    details["Thứ"][0],
                    details["Tiết"][0],
                    details["Phòng"][0],
                    details["Giáo viên"][0]
                ])
                # Write subsequent rows for additional times with shared data as empty strings
                for i in range(1, len(details["Thời gian"])):
                    writer.writerow([
                        "",
                        "",
                        "",
                        "",
                        details["Thời gian"][i],
                        details["Thứ"][i],
                        details["Tiết"][i],
                        details["Phòng"][i],
                        ""
                    ])
                stt += 1

    def add_content(self, new_data):
        name_lopTC = list(new_data.keys())[0]
        rows = []
        try:
            with open(self.csv_file, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                rows = list(reader)
        except FileNotFoundError:
            # Initialize with headers if file doesn't exist
            rows = [["STT", "Tên học phần", "Số tín chỉ", "Tên lớp tín chỉ", "Thời gian", "Thứ", "Tiết", "Phòng", "Giáo viên"]]

        # Determine the next STT value
        next_stt = len(rows)

        # Add new data
        base_data = [
            next_stt,
            new_data[name_lopTC]["Tên học phần"],
            new_data[name_lopTC]["Số tín chỉ"],
            name_lopTC,
            new_data[name_lopTC]["Thời gian"][0],
            new_data[name_lopTC]["Thứ"][0],
            new_data[name_lopTC]["Tiết"][0],
            "",
            new_data[name_lopTC]["Giáo viên"][0]
        ]
        rows.append(base_data)

        # Append subsequent rows with shared data as empty strings
        for index in range(1, len(new_data[name_lopTC]["Thời gian"])):
            row = [
                "",
                "",
                "",
                "",
                new_data[name_lopTC]["Thời gian"][index],
                new_data[name_lopTC]["Thứ"][index],
                new_data[name_lopTC]["Tiết"][index],
                "",
                ""
            ]
            rows.append(row)

        # Write updated content back to the CSV
        with open(self.csv_file, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

    def get_days(self):
        def generate_dates(start_date, end_date):
            current_date = start_date
            while current_date <= end_date:
                yield current_date
                current_date += timedelta(days=1)

        def expand_periods(period_range):
            start, end = map(int, period_range.split("-"))
            return list(range(start, end + 1))

        def get_days_with_periods(timelines, specific_days, lesson_periods):
            result = {}
            for timeline, day, period in zip(timelines, specific_days, lesson_periods):
                start_str, end_str = timeline.split("-")
                start_date = datetime.strptime(start_str, "%d/%m/%Y")
                end_date = datetime.strptime(end_str, "%d/%m/%Y")
                expanded_periods = expand_periods(period)

                for date in generate_dates(start_date, end_date):
                    if date.weekday() == day - 2:  # Match only the specific day of the week
                        date_str = date.strftime("%d/%m/%Y")
                        result[date_str] = expanded_periods

            return result

        content = self.get_content()
        time_summary = {}
        for class_id in content:
            time_summary[class_id] = get_days_with_periods(content[class_id]["Thời gian"],
                                                          content[class_id]["Thứ"],
                                                          content[class_id]["Tiết"])
        return time_summary

    # def save_json(self, output_file):
    #     time_summary = self.get_days()
    #     with open(output_file, "w", encoding="utf-8") as json_file:
    #         json.dump(time_summary, json_file, indent=4, ensure_ascii=False)
    #     print(f"JSON saved to {output_file}")

def find_available(time_hp, time_tkb):
    non_coincidence = {}

    for dk_class, dk_schedule in time_hp.items():
        is_fully_coinciding = False  # Flag to check if any date-period coincides
        
        for date, dk_periods in dk_schedule.items():
            for tkb_class, tkb_schedule in time_tkb.items():
                if date in tkb_schedule:
                    # Check for any overlap in periods
                    if any(period in dk_periods for period in tkb_schedule[date]):
                        is_fully_coinciding = True
                        break
            if is_fully_coinciding:
                break

        # If no date-period coincides for the entire item, add it to the result
        if not is_fully_coinciding:
            non_coincidence[dk_class] = dk_schedule

    return non_coincidence
