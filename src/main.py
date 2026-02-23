"""
Hotel Reservation System - Core Models
Implements Hotel, Customer, and Reservation abstractions
with file-based persistence.
"""
import uuid
import time
from datetime import date
import models.data_handler as data_handler
from models.hotel import Hotel


def main():
    """Main function, starting point of the CLI"""
    start_time = time.time()
    hotels_json = data_handler.load_json(data_handler.HOTELS_FILE)
    hotels = []
    for hotel_id, record in hotels_json.items():
        hotels.append(Hotel.from_dict(record))
    print(hotels)


if __name__ == "__main__":
    main()
