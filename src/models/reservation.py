class Reservation:
    """Represents a room reservation linking a customer to a hotel."""

    STATUS_ACTIVE = "active"
    STATUS_CANCELLED = "cancelled"

    def __init__(
        self,
        reservation_id,
        customer_id,
        hotel_id,
        check_in,
        check_out,
        status=None,
    ):
        self.reservation_id = str(reservation_id)
        self.customer_id = str(customer_id)
        self.hotel_id = str(hotel_id)
        self.check_in = str(check_in)
        self.check_out = str(check_out)
        self.status = status if status else self.STATUS_ACTIVE

    def to_dict(self):
        """Return reservation data as a plain dict."""
        return {
            "reservation_id": self.reservation_id,
            "customer_id": self.customer_id,
            "hotel_id": self.hotel_id,
            "check_in": self.check_in,
            "check_out": self.check_out,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data):
        """Build a Reservation from a dict, raising ValueError on bad data."""
        required = {
            "reservation_id",
            "customer_id",
            "hotel_id",
            "check_in",
            "check_out",
        }
        missing = required - data.keys()
        if missing:
            raise ValueError(f"Reservation record missing fields: {missing}")
        return cls(
            reservation_id=data["reservation_id"],
            customer_id=data["customer_id"],
            hotel_id=data["hotel_id"],
            check_in=data["check_in"],
            check_out=data["check_out"],
            status=data.get("status", cls.STATUS_ACTIVE),
        )

    def display(self):
        """Print reservation information to the console."""
        print(
            f"Reservation ID: {self.reservation_id}\n"
            f"Customer ID   : {self.customer_id}\n"
            f"Hotel ID      : {self.hotel_id}\n"
            f"Check-in      : {self.check_in}\n"
            f"Check-out     : {self.check_out}\n"
            f"Status        : {self.status}"
        )

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    @staticmethod
    def _load_all():
        return _load_json(RESERVATIONS_FILE)

    @staticmethod
    def _save_all(data):
        _save_json(RESERVATIONS_FILE, data)

    @classmethod
    def create(cls, customer_id, hotel_id, check_in, check_out):
        """Persist a new reservation and return the instance."""
        reservation = cls(
            reservation_id=str(uuid.uuid4()),
            customer_id=customer_id,
            hotel_id=hotel_id,
            check_in=str(check_in),
            check_out=str(check_out),
        )
        data = cls._load_all()
        data[reservation.reservation_id] = reservation.to_dict()
        cls._save_all(data)
        return reservation

    @classmethod
    def get(cls, reservation_id):
        """Return a Reservation by ID or None if not found."""
        data = cls._load_all()
        record = data.get(str(reservation_id))
        if record is None:
            return None
        try:
            return cls.from_dict(record)
        except ValueError as exc:
            print(f"ERROR reading reservation {reservation_id}: {exc}")
            return None

    @classmethod
    def get_all(cls):
        """Return list of all valid Reservation instances."""
        data = cls._load_all()
        reservations = []
        for rid, record in data.items():
            try:
                reservations.append(cls.from_dict(record))
            except ValueError as exc:
                print(f"ERROR reading reservation {rid}: {exc}. Skipping record.")
        return reservations

    @classmethod
    def count_active_for_hotel(cls, hotel_id):
        """Return count of active reservations for a given hotel."""
        all_res = cls.get_all()
        return sum(
            1
            for r in all_res
            if r.hotel_id == str(hotel_id) and r.status == cls.STATUS_ACTIVE
        )

    def cancel(self):
        """Mark this reservation as cancelled and persist the change."""
        if self.status == self.STATUS_CANCELLED:
            return False
        self.status = self.STATUS_CANCELLED
        data = self._load_all()
        if self.reservation_id in data:
            data[self.reservation_id]["status"] = self.STATUS_CANCELLED
            self._save_all(data)
        return True

    @classmethod
    def cancel_by_id(cls, reservation_id):
        """Cancel a reservation by ID. Returns True on success, False otherwise."""
        reservation = cls.get(str(reservation_id))
        if reservation is None:
            return False
        return reservation.cancel()

    @classmethod
    def delete(cls, reservation_id):
        """Remove a reservation record entirely."""
        data = cls._load_all()
        reservation_id = str(reservation_id)
        if reservation_id not in data:
            return False
        del data[reservation_id]
        cls._save_all(data)
        return True
