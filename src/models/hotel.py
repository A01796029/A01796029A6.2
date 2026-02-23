import uuid

from .reservation import Reservation
from models.data_handler import (HOTELS_FILE, load_json, save_json)

class Hotel:
    """Represents a hotel with rooms and reservations."""

    def __init__(self, hotel_id, name, address, total_rooms, phone=""):
        if not isinstance(total_rooms, int) or total_rooms <= 0:
            raise ValueError("total_rooms must be a positive integer.")
        self.hotel_id = str(hotel_id)
        self.name = str(name)
        self.address = str(address)
        self.total_rooms = total_rooms
        self.phone = str(phone)

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self):
        """Return hotel data as a plain dict."""
        return {
            "hotel_id": self.hotel_id,
            "name": self.name,
            "address": self.address,
            "total_rooms": self.total_rooms,
            "phone": self.phone,
        }

    @classmethod
    def from_dict(cls, data):
        """Build a Hotel instance from a dict, raising ValueError on bad data."""
        required = {"hotel_id", "name", "address", "total_rooms"}
        missing = required - data.keys()
        if missing:
            raise ValueError(f"Hotel record missing fields: {missing}")
        return cls(
            hotel_id=data["hotel_id"],
            name=data["name"],
            address=data["address"],
            total_rooms=data["total_rooms"],
            phone=data.get("phone", ""),
        )

    def display(self):
        """Print hotel information to the console."""
        print(
            f"Hotel ID   : {self.hotel_id}\n"
            f"Name       : {self.name}\n"
            f"Address    : {self.address}\n"
            f"Total Rooms: {self.total_rooms}\n"
            f"Phone      : {self.phone}"
        )

    # ------------------------------------------------------------------
    # CRUD operations (class-level)
    # ------------------------------------------------------------------
    @staticmethod
    def _load_all():
        print(f"Loading hotels from {HOTELS_FILE}...")
        return load_json(HOTELS_FILE)

    @staticmethod
    def _save_all(data):
        save_json(HOTELS_FILE, data)

    @classmethod
    def create(cls, name, address, total_rooms, phone=""):
        """Persist a new hotel and return the instance."""
        hotel = cls(
            hotel_id=str(uuid.uuid4()),
            name=name,
            address=address,
            total_rooms=total_rooms,
            phone=phone,
        )
        data = cls._load_all()
        data[hotel.hotel_id] = hotel.to_dict()
        cls._save_all(data)
        return hotel

    @classmethod
    def get(cls, hotel_id):
        """Return a Hotel by ID or None if not found."""
        data = cls._load_all()
        record = data.get(str(hotel_id))
        if record is None:
            return None
        try:
            return cls.from_dict(record)
        except ValueError as exc:
            print(f"ERROR reading hotel {hotel_id}: {exc}")
            return None

    @classmethod
    def get_all(cls):
        """Return list of all valid Hotel instances."""
        data = cls._load_all()
        hotels = []
        for hid, record in data.items():
            try:
                hotels.append(cls.from_dict(record))
            except ValueError as exc:
                print(f"ERROR reading hotel {hid}: {exc}. Skipping record.")
        return hotels

    @classmethod
    def delete(cls, hotel_id):
        """Remove a hotel by ID. Returns True if deleted, False if not found."""
        data = cls._load_all()
        hotel_id = str(hotel_id)
        if hotel_id not in data:
            return False
        del data[hotel_id]
        cls._save_all(data)
        return True

    @classmethod
    def modify(cls, hotel_id, **kwargs):
        """Update allowed fields for a hotel. Returns updated Hotel or None."""
        allowed = {"name", "address", "total_rooms", "phone"}
        data = cls._load_all()
        hotel_id = str(hotel_id)
        if hotel_id not in data:
            return None
        record = data[hotel_id]
        for key, value in kwargs.items():
            if key in allowed:
                record[key] = value
        try:
            hotel = cls.from_dict(record)
        except ValueError as exc:
            print(f"ERROR modifying hotel {hotel_id}: {exc}")
            return None
        data[hotel_id] = hotel.to_dict()
        cls._save_all(data)
        return hotel

    # ------------------------------------------------------------------
    # Room availability helpers
    # ------------------------------------------------------------------

    def available_rooms(self):
        """Return number of rooms not currently reserved."""
        active = Reservation.count_active_for_hotel(self.hotel_id)
        return self.total_rooms - active

    def reserve_room(self, customer_id, check_in, check_out):
        """
        Create a reservation for this hotel.
        Returns the Reservation or raises ValueError if no rooms available.
        """
        if self.available_rooms() <= 0:
            raise ValueError(f"No available rooms in hotel {self.hotel_id}.")
        return Reservation.create(
            customer_id=customer_id,
            hotel_id=self.hotel_id,
            check_in=check_in,
            check_out=check_out,
        )

    def cancel_reservation(self, reservation_id):
        """Cancel a reservation associated with this hotel."""
        reservation = Reservation.get(reservation_id)
        if reservation is None:
            raise ValueError(f"Reservation {reservation_id} not found.")
        if reservation.hotel_id != self.hotel_id:
            raise ValueError(
                f"Reservation {reservation_id} does not belong to hotel {self.hotel_id}."
            )
        return reservation.cancel()

