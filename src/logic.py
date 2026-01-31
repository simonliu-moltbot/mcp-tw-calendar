import requests
import datetime
import sys
from typing import Dict, Any, List, Optional

# Constants
# Using a reliable community mirror for Taiwan Calendar data as government URLs often rotate UUIDs.
# Fallback or primary: ruyut/TaiwanCalendar is a standard widely used by developers.
BASE_URL = "https://cdn.jsdelivr.net/gh/ruyut/TaiwanCalendar/data/{year}.json"

def fetch_calendar_data(year: int) -> List[Dict[str, Any]]:
    """
    Fetch the calendar data for the given year.
    Returns a list of daily info objects.
    """
    url = BASE_URL.format(year=year)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        sys.stderr.write(f"[ERROR] Failed to fetch calendar for {year}: {e}\n")
        return []

def get_date_info(date_str: str) -> Dict[str, Any]:
    """
    Get info for a specific date (YYYYMMDD or YYYY-MM-DD).
    """
    # Normalize date
    clean_date = date_str.replace("-", "")
    if len(clean_date) != 8:
        return {"error": "Invalid date format. Use YYYYMMDD or YYYY-MM-DD"}
    
    year = int(clean_date[:4])
    data = fetch_calendar_data(year)
    
    for day in data:
        # Source format usually: {"date": "20260101", "isHoliday": true, "description": "Founding Day"}
        if day.get("date") == clean_date:
            return {
                "date": clean_date,
                "is_holiday": day.get("isHoliday", False),
                "description": day.get("description", ""),
                "week": day.get("week", ""),
                "raw": day
            }
            
    # Default fallback if not found (assume workday if weekday, etc, but safest to say 'No Data')
    return {"date": clean_date, "status": "No specific data found (might be regular day)"}

def get_upcoming_holidays(limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get the next N holidays from today.
    """
    now = datetime.datetime.now()
    current_year = now.year
    
    # Fetch this year and next year to be safe
    data = fetch_calendar_data(current_year)
    data += fetch_calendar_data(current_year + 1)
    
    holidays = []
    today_str = now.strftime("%Y%m%d")
    
    for day in data:
        if day.get("date") >= today_str and day.get("isHoliday") is True:
            holidays.append({
                "date": day.get("date"),
                "description": day.get("description"),
                "week": day.get("week")
            })
            if len(holidays) >= limit:
                break
                
    return holidays

def is_workday(date_str: str) -> Dict[str, Any]:
    """
    Check if a date is a workday.
    """
    info = get_date_info(date_str)
    if "error" in info:
        return info
        
    is_holiday = info.get("is_holiday", False)
    # If is_holiday is True -> Not a workday
    # If is_holiday is False -> Workday
    
    return {
        "date": info.get("date"),
        "is_workday": not is_holiday,
        "reason": info.get("description", "Regular Day")
    }
