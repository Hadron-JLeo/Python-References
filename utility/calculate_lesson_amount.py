from datetime import datetime
from collections import defaultdict


times = ''
hourly_wage = ''


def process_time_ranges(lines: list[str]) -> tuple[int, int, dict]:
    total_minutes = 0
    minutes_by_month = defaultdict(int)
    fmt = "%H:%M"
    
    for line in lines:
        try:
            # Example line: "21.10 17:00-20:15"
            date_str, time_range = line.split(maxsplit=1)
            day, month = map(int, date_str.split("."))
            start_str, end_str = time_range.split("-")
            start_str, end_str = start_str.strip(), end_str.strip()
            
            start_time = datetime.strptime(start_str, fmt)
            end_time = datetime.strptime(end_str, fmt)
            
            minutes = int((end_time - start_time).total_seconds() // 60)
            total_minutes += minutes
            minutes_by_month[month] += minutes
        except Exception as e:
            print(f"Skipping line (bad format): {line} | Error: {e}")
    
    total_sessions = total_minutes // 45
    leftover = total_minutes % 45
    
    sessions_by_month = {
        month: (minutes // 45, minutes % 45)
        for month, minutes in minutes_by_month.items()
    }
    
    return total_sessions, leftover, sessions_by_month


if __name__ == "__main__":
    print("Starting Script")
    lines = times.splitlines()
    lines = list(filter(None, lines))


    total_sessions, leftover, sessions_by_month = process_time_ranges(lines)
    
    print(f"\n=== Overall ===")
    print(f"Total 45-minute sessions: {total_sessions}")
    print(f"Leftover minutes: {leftover}")
    
    print(f"\n=== By Month ===")
    for month, (sessions, leftover) in sorted(sessions_by_month.items()):
        print(f"Month {month:02d}: {sessions} sessions, {leftover} leftover minutes")
