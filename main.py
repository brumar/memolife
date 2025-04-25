import csv
import datetime
from icalendar import Calendar, Event
from dateutil.relativedelta import relativedelta
import calendar

def create_memory_calendar(word_associations_file, output_file, start_date, end_date):
    """
    Creates an ICS calendar file for memory training based on number-word associations.
    
    Args:
        word_associations_file (str): Path to CSV file with number-word associations
        output_file (str): Path to save the ICS file
        start_date (datetime): Starting date for the calendar
        end_date (datetime): Ending date for the calendar
    """
    # Load number-word associations
    associations = {}
    with open(word_associations_file, 'r') as f:
        reader = csv.reader(f, delimiter=',')  # Using comma as delimiter
        for row in reader:
            if len(row) >= 2:
                number = row[0].strip()
                words = [word.strip() for word in row[1:] if word.strip()]
                associations[number] = words
    
    # Create calendar
    cal = Calendar()
    cal.add('prodid', '-//Memory Calendar//EN')
    cal.add('version', '2.0')
    
    # Track year for numbering
    start_year = start_date.year
    
    current_date = start_date
    while current_date <= end_date:
        # Generate day number code
        # First digit is quarter (0-3), last two digits are day of month
        quarter = (current_date.month - 1) // 3
        day_of_month = current_date.day
        
        # Base day code for current date
        base_day_code = f"{quarter}{day_of_month:02d}"
        
        # Add 400 for year 2
        year_offset = 400 * (current_date.year - start_year)
        day_code_int = int(base_day_code) + year_offset
        day_code = f"{day_code_int}"  # No leading zeros
        
        # Ensure it's still 3 digits for the calendar
        day_code_display = f"{day_code_int:03d}"
        
        # Get associated words (if available)
        associated_words = associations.get(day_code_display, ["No association"])
        primary_word = associated_words[0] if associated_words else "No association"
        alt_words = associated_words[1:] if len(associated_words) > 1 else []
        
        # Create event
        event = Event()
        event.add('summary', f"{day_code_display} {primary_word}")
        
        # Format description according to requirements
        description = f"Other Possibilities\n=============\n{', '.join(alt_words)}\n\n"
        description += f"To Review\n=======\n"
        
        # Add review instructions for previous 3 days (J-3 to J-1), ordered from oldest to newest
        review_days = []
        for days_back in range(3, 0, -1):  # From 3 days back to 1 day back (oldest to newest)
            prev_day = current_date - datetime.timedelta(days=days_back)
            prev_quarter = (prev_day.month - 1) // 3
            prev_base_day_code = f"{prev_quarter}{prev_day.day:02d}"
            
            # Apply year offset for previous days too
            prev_year_offset = 400 * (prev_day.year - start_year)
            prev_day_code_int = int(prev_base_day_code) + prev_year_offset
            prev_day_code = f"{prev_day_code_int:03d}"
            
            # Get the word for this review day
            prev_day_word = associations.get(prev_day_code, ["No association"])[0]
            review_days.append(f"{prev_day_code} {prev_day_word}")
        
        description += f"{', '.join(review_days)}\n\n"
        description += f"Day Logs\n======\n"
        
        # Add special review instructions
        # Sunday: review whole week
        if current_date.weekday() == 6:  # Sunday
            # Get codes for the past week (ordered from oldest to newest)
            week_codes = []
            for days_back in range(7, 0, -1):  # Past 7 days, oldest to newest
                week_day = current_date - datetime.timedelta(days=days_back)
                week_quarter = (week_day.month - 1) // 3
                week_base_code = f"{week_quarter}{week_day.day:02d}"
                
                # Apply year offset
                week_year_offset = 400 * (week_day.year - start_year)
                week_code_int = int(week_base_code) + week_year_offset
                week_code = f"{week_code_int:03d}"
                
                # Get the word for this day
                week_day_word = associations.get(week_code, ["No association"])[0]
                week_codes.append(f"{week_code} {week_day_word}")
            
            description += f"\nSUNDAY REVIEW: {', '.join(week_codes)}"
            
        # Wednesday: review week -2 and week -3
        if current_date.weekday() == 2:  # Wednesday
            # Week -3 (oldest)
            week_minus_3_codes = []
            for days_back in range(21, 14, -1):  # Week -3, ordered from oldest to newest
                week3_day = current_date - datetime.timedelta(days=days_back)
                week3_quarter = (week3_day.month - 1) // 3
                week3_base_code = f"{week3_quarter}{week3_day.day:02d}"
                
                # Apply year offset
                week3_year_offset = 400 * (week3_day.year - start_year)
                week3_code_int = int(week3_base_code) + week3_year_offset
                week3_code = f"{week3_code_int:03d}"
                
                # Get the word for this day
                week3_day_word = associations.get(week3_code, ["No association"])[0]
                week_minus_3_codes.append(f"{week3_code} {week3_day_word}")
            
            # Week -2 (newer)
            week_minus_2_codes = []
            for days_back in range(14, 7, -1):  # Week -2, ordered from oldest to newest
                week2_day = current_date - datetime.timedelta(days=days_back)
                week2_quarter = (week2_day.month - 1) // 3
                week2_base_code = f"{week2_quarter}{week2_day.day:02d}"
                
                # Apply year offset
                week2_year_offset = 400 * (week2_day.year - start_year)
                week2_code_int = int(week2_base_code) + week2_year_offset
                week2_code = f"{week2_code_int:03d}"
                
                # Get the word for this day
                week2_day_word = associations.get(week2_code, ["No association"])[0]
                week_minus_2_codes.append(f"{week2_code} {week2_day_word}")
            
            # Add both weeks to description, oldest first
            description += f"\nWEDNESDAY REVIEW: Week -3: {', '.join(week_minus_3_codes)}, Week -2: {', '.join(week_minus_2_codes)}"
            
        # Last Friday of the month: review month -2 and month -1
        month_calendar = calendar.monthcalendar(current_date.year, current_date.month)
        last_friday = max(week[4] for week in month_calendar if week[4] > 0)
        if current_date.day == last_friday and current_date.weekday() == 4:
            # Month -2 (oldest)
            month_minus_2 = current_date - relativedelta(months=2)
            month_minus_2_quarter = (month_minus_2.month - 1) // 3
            month_minus_2_start_base = f"{month_minus_2_quarter}01"
            month_minus_2_end_base = f"{month_minus_2_quarter}{calendar.monthrange(month_minus_2.year, month_minus_2.month)[1]:02d}"
            
            # Apply year offset
            month_minus_2_year_offset = 400 * (month_minus_2.year - start_year)
            month_minus_2_start_int = int(month_minus_2_start_base) + month_minus_2_year_offset
            month_minus_2_end_int = int(month_minus_2_end_base) + month_minus_2_year_offset
            month_minus_2_start = f"{month_minus_2_start_int:03d}"
            month_minus_2_end = f"{month_minus_2_end_int:03d}"
            
            # Month -1 (newer)
            month_minus_1 = current_date - relativedelta(months=1)
            month_minus_1_quarter = (month_minus_1.month - 1) // 3
            month_minus_1_start_base = f"{month_minus_1_quarter}01"
            month_minus_1_end_base = f"{month_minus_1_quarter}{calendar.monthrange(month_minus_1.year, month_minus_1.month)[1]:02d}"
            
            # Apply year offset
            month_minus_1_year_offset = 400 * (month_minus_1.year - start_year)
            month_minus_1_start_int = int(month_minus_1_start_base) + month_minus_1_year_offset
            month_minus_1_end_int = int(month_minus_1_end_base) + month_minus_1_year_offset
            month_minus_1_start = f"{month_minus_1_start_int:03d}"
            month_minus_1_end = f"{month_minus_1_end_int:03d}"
            
            description += f"\nLAST FRIDAY REVIEW: Month -2: {month_minus_2_start} to {month_minus_2_end}, Month -1: {month_minus_1_start} to {month_minus_1_end}"
            
        # First day of season: review season -2
        if current_date.day == 1 and current_date.month in [1, 4, 7, 10]:
            # Season -2
            season_minus_2_start = current_date - relativedelta(months=6)
            season_minus_2_end = current_date - relativedelta(months=4)
            season_minus_2_start_quarter = (season_minus_2_start.month - 1) // 3
            season_minus_2_end_quarter = (season_minus_2_end.month - 1) // 3
            
            # Base codes
            season_minus_2_start_base = f"{season_minus_2_start_quarter}01"
            season_minus_2_end_base = f"{season_minus_2_end_quarter}{calendar.monthrange(season_minus_2_end.year, season_minus_2_end.month)[1]:02d}"
            
            # Apply year offset
            season_minus_2_start_year_offset = 400 * (season_minus_2_start.year - start_year)
            season_minus_2_end_year_offset = 400 * (season_minus_2_end.year - start_year)
            season_minus_2_start_int = int(season_minus_2_start_base) + season_minus_2_start_year_offset
            season_minus_2_end_int = int(season_minus_2_end_base) + season_minus_2_end_year_offset
            season_minus_2_start_code = f"{season_minus_2_start_int:03d}"
            season_minus_2_end_code = f"{season_minus_2_end_int:03d}"
            
            description += f"\nSEASON START REVIEW: Season -2: {season_minus_2_start_code} to {season_minus_2_end_code}"
        
        event.add('description', description)
        event.add('dtstart', current_date)
        event.add('dtend', current_date + datetime.timedelta(days=1))
        event.add('dtstamp', datetime.datetime.now())
        
        # Add event to calendar
        cal.add_component(event)
        
        # Move to next day
        current_date += datetime.timedelta(days=1)
    
    # Write to file
    with open(output_file, 'wb') as f:
        f.write(cal.to_ical())
    
    return output_file

# Generate a sample calendar entry to show the format
def generate_sample_entries():
    """Generate sample calendar entries to demonstrate the format"""
    # Create a simple sample associations dictionary
    sample_associations = {
        "001": ["apple", "fruit", "red"],
        "002": ["boat", "sailing", "water"],
        "003": ["cat", "feline", "pet"],
        "031": ["zebra", "stripes", "safari"],
        "101": ["diamond", "gem", "sparkle"],
        "131": ["elephant", "trunk", "large"],  # May 1st
        "201": ["eagle", "bird", "predator"],
        "401": ["window", "glass", "view"]      # Year 2, Jan 1
    }
    
    # Create a calendar with sample entries
    cal = Calendar()
    cal.add('prodid', '-//Memory Calendar Sample//EN')
    cal.add('version', '2.0')
    
    # Sample dates for demonstration
    start_year = 2025
    sample_dates = [
        (datetime.datetime(2025, 1, 1), 0),    # Regular day (001) - Year 1
        (datetime.datetime(2025, 5, 1), 0),    # May 1st (131) - Year 1
        (datetime.datetime(2025, 1, 5), 0),    # Sunday weekly review - Year 1
        (datetime.datetime(2025, 1, 31), 0),   # Last Friday monthly review - Year 1
        (datetime.datetime(2025, 4, 1), 0),    # First day of season review - Year 1
        (datetime.datetime(2026, 1, 1), 1)     # Year 2, Jan 1 (401)
    ]
    
    for date, year_offset in sample_dates:
        quarter = (date.month - 1) // 3
        day_of_month = date.day
        
        # Base day code
        base_day_code = f"{quarter}{day_of_month:02d}"
        
        # Add year offset (400 for year 2)
        day_code_int = int(base_day_code) + (400 * year_offset)
        day_code = f"{day_code_int:03d}"
        
        # Get associated words (if available)
        associated_words = sample_associations.get(day_code, ["No association"])
        primary_word = associated_words[0] if associated_words else "No association"
        alt_words = associated_words[1:] if len(associated_words) > 1 else []
        
        # Create event
        event = Event()
        event.add('summary', f"{day_code} {primary_word}")
        
        # Format description according to new requirements
        description = f"Other Possibilities\n=============\n{', '.join(alt_words)}\n\n"
        description += f"To Review\n=======\n"
        
        # Add review instructions - ordered from oldest to newest
        review_days = []
        for days_back in range(3, 0, -1):  # From J-3 to J-1 (oldest to newest)
            prev_day = date - datetime.timedelta(days=days_back)
            prev_quarter = (prev_day.month - 1) // 3
            prev_base_code = f"{prev_quarter}{prev_day.day:02d}"
            
            # Apply year offset for the previous day
            prev_year_offset = 400 * (1 if prev_day.year > start_year else 0)
            prev_code_int = int(prev_base_code) + prev_year_offset
            prev_code = f"{prev_code_int:03d}"
            
            # Get word for this day
            prev_word = sample_associations.get(prev_code, ["No association"])[0]
            review_days.append(f"{prev_code} {prev_word}")
        
        description += f"{', '.join(review_days)}\n\n"
        description += f"Day Logs\n======\n"
        
        # Add special review instructions for specific days
        if date.day == 5 and date.month == 1:  # Jan 5 (Sunday)
            description += "\nSUNDAY REVIEW: 003 cat, 004 No association"
            
        if date.day == 31 and date.month == 1:  # Jan 31 (Last Friday)
            description += "\nLAST FRIDAY REVIEW: Month -2: 201 to 231, Month -1: 001 to 031"
            
        if date.day == 1 and date.month == 4:  # Apr 1 (First day of season)
            description += "\nSEASON START REVIEW: Season -2: 001 to 031"
            
        if date.day == 1 and date.month == 1 and year_offset == 1:  # Year 2, Jan 1
            description += "\nSEASON START REVIEW: Season -2: 201 to 231"
        
        event.add('description', description)
        event.add('dtstart', date)
        event.add('dtend', date + datetime.timedelta(days=1))
        event.add('dtstamp', datetime.datetime.now())
        
        # Add event to calendar
        cal.add_component(event)
    
    return cal.to_ical().decode('utf-8')

# Example usage
if __name__ == "__main__":
    # Starting today for 2 years
    start_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + relativedelta(years=2)
    
    create_memory_calendar(
        word_associations_file="number_words.csv",
        output_file="memory_calendar.ics",
        start_date=start_date,
        end_date=end_date
    )
    
    # Generate and show sample entries
    sample_ics = generate_sample_entries()
    print("Sample ICS entries:")
    print(sample_ics)
    
    # Also save sample to file
    with open("sample_memory_calendar.ics", "w") as sample_file:
        sample_file.write(sample_ics)
    print("\nSample calendar saved to 'sample_memory_calendar.ics'")
