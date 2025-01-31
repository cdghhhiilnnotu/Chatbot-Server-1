from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import pandas as pd
import json
import csv
from datetime import datetime, timedelta

@dataclass
class ScheduleEntry:
    """Data class for schedule entry details."""
    credit_count: str
    course_name: str
    times: List[str]
    days: List[str]
    periods: List[str]
    teachers: List[str]
    rooms: List[str]


@dataclass
class CourseEntry:
    """Data class for course entry details."""
    credit_count: str
    course_name: str
    times: List[str]
    days: List[str]
    periods: List[str]
    teachers: List[str]
    student_counts: List[int]

@dataclass
class ExamEntry:
    """Data class for exam entry details."""
    course_code: str
    course_name: str
    credit_count: str
    exam_date: str
    exam_session: str
    exam_time: str
    exam_attempt: str
    exam_period: str
    student_count: str
    exam_room: str
    exam_type: str
    postponed: str

class LichThi:
    """Class for handling exam schedules."""
    
    def __init__(self, csv_file: str):
        """Initialize LichThi with CSV file path."""
        self.csv_file = csv_file
        self.data: Optional[pd.DataFrame] = None
        self.HEADERS = [
            "STT", "Mã học phần", "Tên học phần", "Số tín chỉ",
            "Ngày thi", "Ca thi", "Giờ thi", "Lần thi", "Đợt thi",
            "Số báo danh", "Phòng thi", "Hình thức", "Hoãn thi"
        ]

    def read_data(self) -> None:
        """Read and preprocess CSV data."""
        self.data = pd.read_csv(self.csv_file, encoding='utf-8')
        
        # Convert numeric columns to string type
        numeric_cols = self.data.select_dtypes(include=["float64", "int64"]).columns
        for col in numeric_cols:
            self.data[col] = self.data[col].astype("object")
        
        # Handle missing values
        self.data.fillna("", inplace=True)
        self.HEADERS = self.data.columns

    def get_content(self) -> Dict[int, ExamEntry]:
        """Extract and organize exam content from CSV data."""
        self.read_data()
        exams: Dict[int, ExamEntry] = {}
        
        print(self.data.columns)
        for header in self.HEADERS:
            if header in self.data.columns:
                print(f"{header} exists!")
            else:
                print(f"{header} does not exist!")
        for _, row in self.data.iterrows():
            exam_entry = ExamEntry(
                course_code=row[self.HEADERS[1]],
                course_name=row[self.HEADERS[2]],
                credit_count=row[self.HEADERS[3]],
                exam_date=row[self.HEADERS[4]],
                exam_session=row[self.HEADERS[5]],
                exam_time=row[self.HEADERS[6]],
                exam_attempt=row[self.HEADERS[7]],
                exam_period=row[self.HEADERS[8]],
                student_count=row[self.HEADERS[9]],
                exam_room=row[self.HEADERS[10]],
                exam_type=row[self.HEADERS[11]],
                postponed=row[self.HEADERS[12]]
            )
            exams[int(row[self.HEADERS[0]])] = exam_entry
            
        return exams

    def update_content(self, data: Dict[int, ExamEntry]) -> None:
        """Update CSV with new content."""
        with open(self.csv_file, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.HEADERS)
            self._write_entries(writer, data)

    def _write_entries(self, writer, data: Dict[int, ExamEntry]) -> None:
        """Write exam entries to CSV."""
        for stt, entry in sorted(data.items()):
            writer.writerow([
                stt,
                entry.course_code,
                entry.course_name,
                entry.credit_count,
                entry.exam_date,
                entry.exam_session,
                entry.exam_time,
                entry.exam_attempt,
                entry.exam_period,
                entry.student_count,
                entry.exam_room,
                entry.exam_type,
                entry.postponed
            ])

    def add_entry(self, new_entry: ExamEntry) -> None:
        """Add a new exam entry to the schedule."""
        exams = self.get_content()
        next_stt = max(exams.keys(), default=0) + 1
        exams[next_stt] = new_entry
        self.update_content(exams)

    def delete_entry(self, stt: int) -> None:
        """Delete an exam entry by its STT."""
        exams = self.get_content()
        if stt in exams:
            del exams[stt]
            self.update_content(exams)

    def find_exams_by_date(self, date_str: str) -> Dict[int, ExamEntry]:
        """Find exam entries for a specific date.
        
        Args:
            date_str: Date string in format 'DD/MM/YYYY'
        
        Returns:
            Dictionary of exam entries for the specified date
        """
        try:
            # Validate date format
            datetime.strptime(date_str, "%d/%m/%Y")
            
            exams = self.get_content()
            return {
                stt: entry 
                for stt, entry in exams.items() 
                if entry.exam_date == date_str
            }
        except ValueError:
            raise ValueError("Date must be in format DD/MM/YYYY")

    def find_exams_by_course_code(self, course_code: str) -> Dict[int, ExamEntry]:
        """Find exam entries for a specific course code."""
        exams = self.get_content()
        return {
            stt: entry 
            for stt, entry in exams.items() 
            if entry.course_code == course_code
        }

    def find_exams_by_period(self, period: str) -> Dict[int, ExamEntry]:
        """Find exam entries for a specific exam period."""
        exams = self.get_content()
        return {
            stt: entry 
            for stt, entry in exams.items() 
            if entry.exam_period == period
        }

    def find_postponed_exams(self) -> Dict[int, ExamEntry]:
        """Find all postponed exam entries."""
        exams = self.get_content()
        return {
            stt: entry 
            for stt, entry in exams.items() 
            if entry.postponed
        }

    def get_exam_statistics(self) -> Dict[str, int]:
        """Get basic statistics about the exam schedule."""
        exams = self.get_content()
        return {
            "total_exams": len(exams),
            "morning_sessions": sum(1 for entry in exams.values() if entry.exam_session == "Sáng"),
            "afternoon_sessions": sum(1 for entry in exams.values() if entry.exam_session == "Chiều"),
            "postponed_exams": sum(1 for entry in exams.values() if entry.postponed),
            "written_exams": sum(1 for entry in exams.values() if entry.exam_type == "Thi viết")
        }

class MonHoc:
    """Class for handling course information."""
    
    def __init__(self, csv_file: str):
        """Initialize MonHoc with CSV file path."""
        self.csv_file = csv_file
        self.data: pd.DataFrame | None = None
        self.HEADERS = [
            "STT", "Tên học phần", "Số tín chỉ", "Tên lớp tín chỉ",
            "Thời gian", "Thứ", "Tiết", "Số lượng", "Giáo viên"
        ]

    def read_data(self) -> None:
        """Read and preprocess CSV data."""
        self.data = pd.read_csv(self.csv_file)
        
        # Convert numeric columns to string type
        numeric_cols = self.data.select_dtypes(include=["float64", "int64"]).columns
        for col in numeric_cols:
            self.data[col] = self.data[col].astype("object")
        
        # Handle missing values
        self.data.fillna(method='ffill', inplace=True)
        self.data.fillna("", inplace=True)

    def get_content(self) -> Dict[str, CourseEntry]:
        """Extract and organize course content from CSV data."""
        self.read_data()
        summary: Dict[str, Dict] = {}
        current_class = ""

        for _, row in self.data.iterrows():
            if row["Tên lớp tín chỉ"]:
                current_class = row["Tên lớp tín chỉ"]
            
            if current_class:
                if current_class not in summary:
                    summary[current_class] = {
                        "Số tín chỉ": row["Số tín chỉ"],
                        "Tên học phần": row["Tên học phần"],
                        "Thời gian": [],
                        "Thứ": [],
                        "Tiết": [],
                        "Giáo viên": set(),
                        "Số lượng": []
                    }
                
                self._update_entry(summary[current_class], row)

        # Convert to CourseEntry objects
        return {
            class_id: CourseEntry(
                credit_count=details["Số tín chỉ"],
                course_name=details["Tên học phần"],
                times=details["Thời gian"],
                days=details["Thứ"],
                periods=details["Tiết"],
                teachers=list(details["Giáo viên"]),
                student_counts=details["Số lượng"]
            )
            for class_id, details in summary.items()
        }

    def _update_entry(self, entry: Dict[str, Any], row: pd.Series) -> None:
        """Update entry dictionary with row data."""
        entry["Thời gian"].append(row["Thời gian"])
        entry["Thứ"].append(row["Thứ"])
        entry["Tiết"].append(row["Tiết"])
        entry["Số lượng"].append(row["Số lượng"])
        if row["Giáo viên"]:
            entry["Giáo viên"].add(row["Giáo viên"])

    def success_submit(self) -> None:
        """Write processed data back to CSV."""
        data = self.get_content()
        
        with open(self.csv_file, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.HEADERS)
            self._write_entries(writer, data)

    def _write_entries(self, writer, data: Dict[str, CourseEntry]) -> None:
        """Write course entries to CSV."""
        for stt, (class_code, entry) in enumerate(data.items(), 1):
            # Write main row
            writer.writerow([
                stt,
                entry.course_name,
                entry.credit_count,
                class_code,
                entry.times[0],
                entry.days[0],
                entry.periods[0],
                entry.student_counts[0],
                entry.teachers[0]
            ])

            # Write additional time slots
            for i in range(1, len(entry.times)):
                writer.writerow([
                    "", "", "", "",
                    entry.times[i],
                    entry.days[i],
                    entry.periods[i],
                    entry.student_counts[i] - 1,
                    ""
                ])

    @staticmethod
    def _generate_dates(start_date: datetime, end_date: datetime) -> List[datetime]:
        """Generate sequence of dates between start and end dates."""
        dates = []
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)
        return dates

    @staticmethod
    def _expand_periods(period_range: str) -> List[int]:
        """Convert period range string to list of integers."""
        start, end = map(int, period_range.split("-"))
        return list(range(start, end + 1))

    def _get_days_with_periods(self, 
                             timelines: List[str], 
                             specific_days: List[int], 
                             lesson_periods: List[str]) -> Dict[str, List[int]]:
        """Generate dictionary of dates and their corresponding periods."""
        result: Dict[str, List[int]] = {}
        
        for timeline, day, period in zip(timelines, specific_days, lesson_periods):
            start_str, end_str = timeline.split("-")
            start_date = datetime.strptime(start_str, "%d/%m/%Y")
            end_date = datetime.strptime(end_str, "%d/%m/%Y")
            expanded_periods = self._expand_periods(period)

            for date in self._generate_dates(start_date, end_date):
                if date.weekday() == day - 2:  # Convert to Python's weekday format
                    date_str = date.strftime("%d/%m/%Y")
                    result[date_str] = expanded_periods

        return result

    def get_days(self) -> Dict[str, Dict[str, List[int]]]:
        """Get days and periods for courses with multiple sessions."""
        content = self.get_content()
        time_summary: Dict[str, Dict[str, List[int]]] = {}
        
        for class_id, entry in content.items():
            if entry.student_counts[0] > 1:
                time_summary[class_id] = self._get_days_with_periods(
                    entry.times,
                    [int(day) for day in entry.days],
                    entry.periods
                )
        
        return time_summary

class TKB:
    """Class for handling educational schedules (Thời Khóa Biểu)."""
    
    def __init__(self, csv_file: str):
        """Initialize TKB with CSV file path."""
        self.csv_file = csv_file
        self.data: Optional[pd.DataFrame] = None
        self.HEADERS = [
            "STT", "Tên học phần", "Số tín chỉ", "Tên lớp tín chỉ",
            "Thời gian", "Thứ", "Tiết", "Phòng", "Giáo viên"
        ]

    def read_data(self) -> None:
        """Read and preprocess CSV data."""
        self.data = pd.read_csv(self.csv_file)
        
        # Convert numeric columns to string type
        numeric_cols = self.data.select_dtypes(include=["float64", "int64"]).columns
        for col in numeric_cols:
            self.data[col] = self.data[col].astype("object")
        
        # Handle missing values
        self.data.fillna(method='ffill', inplace=True)
        self.data.fillna("", inplace=True)

    def get_content(self) -> Dict[str, ScheduleEntry]:
        """Extract and organize schedule content from CSV data."""
        self.read_data()
        summary: Dict[str, Dict] = {}
        current_class = ""

        for _, row in self.data.iterrows():
            if row["Tên lớp tín chỉ"]:
                current_class = row["Tên lớp tín chỉ"]
            
            if current_class:
                if current_class not in summary:
                    summary[current_class] = {
                        "Số tín chỉ": row["Số tín chỉ"],
                        "Tên học phần": row["Tên học phần"],
                        "Thời gian": [],
                        "Thứ": [],
                        "Tiết": [],
                        "Giáo viên": set(),
                        "Phòng": []
                    }
                
                self._update_entry(summary[current_class], row)

        # Convert to ScheduleEntry objects
        return {
            class_id: ScheduleEntry(
                credit_count=details["Số tín chỉ"],
                course_name=details["Tên học phần"],
                times=details["Thời gian"],
                days=details["Thứ"],
                periods=details["Tiết"],
                teachers=list(details["Giáo viên"]),
                rooms=details["Phòng"]
            )
            for class_id, details in summary.items()
        }

    def _update_entry(self, entry: Dict[str, Any], row: pd.Series) -> None:
        """Update entry dictionary with row data."""
        entry["Thời gian"].append(row["Thời gian"])
        entry["Thứ"].append(row["Thứ"])
        entry["Tiết"].append(row["Tiết"])
        entry["Phòng"].append(row["Phòng"])
        if row["Giáo viên"]:
            entry["Giáo viên"].add(row["Giáo viên"])

    def delete_content(self, course_code: str) -> None:
        """Delete content for a specific course code."""
        schedule = self.get_content()
        updated_schedule = {
            class_id: entry 
            for class_id, entry in schedule.items()
            if not class_id.startswith(f"{course_code}_")
        }
        self.update_content(updated_schedule)

    def update_content(self, data: Dict[str, ScheduleEntry]) -> None:
        """Update CSV with new content."""
        with open(self.csv_file, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.HEADERS)
            self._write_entries(writer, data)

    def _write_entries(self, writer, data: Dict[str, ScheduleEntry]) -> None:
        """Write schedule entries to CSV."""
        for stt, (class_code, entry) in enumerate(data.items(), 1):
            # Write main row
            writer.writerow([
                stt,
                entry.course_name,
                entry.credit_count,
                class_code,
                entry.times[0],
                entry.days[0],
                entry.periods[0],
                entry.rooms[0],
                entry.teachers[0] if entry.teachers else ""
            ])

            # Write additional time slots
            for i in range(1, len(entry.times)):
                writer.writerow([
                    "", "", "", "",
                    entry.times[i],
                    entry.days[i],
                    entry.periods[i],
                    entry.rooms[i],
                    ""
                ])

    def add_content(self, new_data: Dict[str, ScheduleEntry]) -> None:
        """Add new content to the schedule."""
        class_code = next(iter(new_data))
        entry = new_data[class_code]
        
        try:
            with open(self.csv_file, mode='r', encoding='utf-8') as file:
                rows = list(csv.reader(file))
        except FileNotFoundError:
            rows = [self.HEADERS]

        next_stt = len(rows)

        # Add main row
        rows.append([
            next_stt,
            entry.course_name,
            entry.credit_count,
            class_code,
            entry.times[0],
            entry.days[0],
            entry.periods[0],
            "",
            entry.teachers[0] if entry.teachers else ""
        ])

        # Add additional time slots
        for i in range(1, len(entry.times)):
            rows.append([""] * 4 + [
                entry.times[i],
                entry.days[i],
                entry.periods[i],
                "",
                ""
            ])

        with open(self.csv_file, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

    @staticmethod
    def _expand_periods(period_range: str) -> List[int]:
        """Convert period range string to list of integers."""
        start, end = map(int, period_range.split("-"))
        return list(range(start, end + 1))

    @staticmethod
    def _generate_dates(start_date: datetime, end_date: datetime):
        """Generate sequence of dates between start and end dates."""
        current_date = start_date
        while current_date <= end_date:
            yield current_date
            current_date += timedelta(days=1)

    def generate_schedule(self) -> Dict[str, Dict[str, Any]]:
        """Generate detailed schedule with all time slots."""
        self.read_data()
        schedule: Dict[str, Dict[str, Any]] = {}

        for _, row in self.data.iterrows():
            class_id = row["Tên lớp tín chỉ"]
            if class_id and class_id not in schedule:
                schedule[class_id] = {
                    "Số tín chỉ": row["Số tín chỉ"],
                    "Tên học phần": row["Tên học phần"],
                    "Thời gian - Tiết": {},
                    "Giáo viên": [],
                    "Phòng": []
                }

            if class_id:
                self._process_schedule_row(schedule[class_id], row)

        return schedule

    def _process_schedule_row(self, schedule_entry: Dict[str, Any], row: pd.Series) -> None:
        """Process a single row for schedule generation."""
        if all(row[field] for field in ["Thời gian", "Thứ", "Tiết"]):
            start_str, end_str = row["Thời gian"].split("-")
            start_date = datetime.strptime(start_str.strip(), "%d/%m/%Y")
            end_date = datetime.strptime(end_str.strip(), "%d/%m/%Y")
            day_of_week = int(row["Thứ"]) - 2  # Convert to Python's weekday format
            periods = self._expand_periods(row["Tiết"])

            for date in self._generate_dates(start_date, end_date):
                if date.weekday() == day_of_week:
                    date_str = date.strftime("%d/%m/%Y")
                    if date_str not in schedule_entry["Thời gian - Tiết"]:
                        schedule_entry["Thời gian - Tiết"][date_str] = []
                    schedule_entry["Thời gian - Tiết"][date_str].extend(periods)

        # Update teacher and room information
        if row["Giáo viên"] and row["Giáo viên"] not in schedule_entry["Giáo viên"]:
            schedule_entry["Giáo viên"].append(row["Giáo viên"])
        if row["Phòng"] and row["Phòng"] not in schedule_entry["Phòng"]:
            schedule_entry["Phòng"].append(row["Phòng"])

    def save_to_json(self, json_file: str) -> None:
        """Save schedule to JSON file."""
        schedule = self.generate_schedule()
        with open(json_file, mode="w", encoding="utf-8") as file:
            json.dump(schedule, file, ensure_ascii=False, indent=4)

    def find_item_by_date(self, date_str: str) -> Dict[str, Dict[str, Any]]:
        """Find scheduled items for a specific date."""
        schedule = self.generate_schedule()
        # print(date_str)
        # print(schedule["TH4309_20CN1"]["Thời gian - Tiết"][date_str])
        # result = {}
        # for class_id, details in schedule.items():
        #     if date_str in details["Thời gian - Tiết"]:
        #         result[class_id] = {
        #             "Số tín chỉ": details["Số tín chỉ"],
        #             "Tên học phần": details["Tên học phần"],
        #             "Giáo viên": details["Giáo viên"],
        #             "Phòng": details["Phòng"],
        #             "Tiết": details["Thời gian - Tiết"][date_str]
        #         }
        #         print(result)
            # print(class_id)
            # print(date_str in details["Thời gian - Tiết"])

        return {
            class_id: {
                "Số tín chỉ": details["Số tín chỉ"],
                "Tên học phần": details["Tên học phần"],
                "Giáo viên": details["Giáo viên"],
                "Phòng": details["Phòng"],
                "Tiết": details["Thời gian - Tiết"][date_str]
            }
            for class_id, details in schedule.items()
            if date_str in details["Thời gian - Tiết"]
        }
    
    def get_days(self) -> Dict[str, Dict[str, List[int]]]:
        """
        Generate a summary of dates and periods for each class based on schedules.

        Returns:
            Dict[str, Dict[str, List[int]]]: A dictionary mapping class IDs to their respective
                                            dates and periods.
        """
        def generate_dates(start_date, end_date):
            """Generate a sequence of dates between start_date and end_date."""
            current_date = start_date
            while current_date <= end_date:
                yield current_date
                current_date += timedelta(days=1)

        def expand_periods(period_range: str) -> List[int]:
            """Expand a range of periods into a list of integers."""
            start, end = map(int, period_range.split("-"))
            return list(range(start, end + 1))

        def get_days_with_periods(timelines, specific_days, lesson_periods) -> Dict[str, List[int]]:
            """
            Get a mapping of dates to periods for specific days and periods.

            Args:
                timelines (List[str]): A list of date ranges in the format "dd/mm/yyyy-dd/mm/yyyy".
                specific_days (List[int]): A list of days (e.g., 2 for Monday).
                lesson_periods (List[str]): A list of period ranges (e.g., "1-3").

            Returns:
                Dict[str, List[int]]: A mapping of dates to the list of periods.
            """
            result = {}
            for timeline, day, period in zip(timelines, specific_days, lesson_periods):
                start_str, end_str = timeline.split("-")
                start_date = datetime.strptime(start_str, "%d/%m/%Y")
                end_date = datetime.strptime(end_str, "%d/%m/%Y")
                expanded_periods = expand_periods(period)

                for date in generate_dates(start_date, end_date):
                    if date.weekday() == day - 2:  # Match only the specific day of the week
                        date_str = date.strftime("%d/%m/%Y")
                        if date_str not in result:
                            result[date_str] = []
                        result[date_str].extend(expanded_periods)

            return result

        # Extract schedule content
        content = self.get_content()
        time_summary = {}
        for class_id, schedule in content.items():
            time_summary[class_id] = get_days_with_periods(
                schedule.times, 
                list(map(int, schedule.days)), 
                schedule.periods
            )

        return time_summary
    

