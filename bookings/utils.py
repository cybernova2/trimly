from datetime import datetime, timedelta

def generate_time_slots(opening_time, closing_time, duration_minutes):
    slots = []

    current = datetime.combine(datetime.today(), opening_time)
    end = datetime.combine(datetime.today(), closing_time)

    while current + timedelta(minutes=duration_minutes) <= end:
        slots.append(current.time())
        current += timedelta(minutes=duration_minutes)

    return slots
