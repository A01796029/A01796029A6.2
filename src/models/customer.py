class Customer:
    """Represents a hotel customer."""

    def __init__(self, customer_id, first_name, last_name, email, phone=""):
        self.customer_id = str(customer_id)
        self.first_name = str(first_name)
        self.last_name = str(last_name)
        self.email = str(email)
        self.phone = str(phone)

    def to_dict(self):
        """Return customer data as a plain dict."""
        return {
            "customer_id": self.customer_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
        }

    @classmethod
    def from_dict(cls, data):
        """Build a Customer from a dict, raising ValueError on bad data."""
        required = {"customer_id", "first_name", "last_name", "email"}
        missing = required - data.keys()
        if missing:
            raise ValueError(f"Customer record missing fields: {missing}")
        return cls(
            customer_id=data["customer_id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            phone=data.get("phone", ""),
        )

    def display(self):
        """Print customer information to the console."""
        print(
            f"Customer ID: {self.customer_id}\n"
            f"Name       : {self.first_name} {self.last_name}\n"
            f"Email      : {self.email}\n"
            f"Phone      : {self.phone}"
        )

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    @staticmethod
    def _load_all():
        return _load_json(CUSTOMERS_FILE)

    @staticmethod
    def _save_all(data):
        _save_json(CUSTOMERS_FILE, data)

    @classmethod
    def create(cls, first_name, last_name, email, phone=""):
        """Persist a new customer and return the instance."""
        customer = cls(
            customer_id=str(uuid.uuid4()),
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
        )
        data = cls._load_all()
        data[customer.customer_id] = customer.to_dict()
        cls._save_all(data)
        return customer

    @classmethod
    def get(cls, customer_id):
        """Return a Customer by ID or None if not found."""
        data = cls._load_all()
        record = data.get(str(customer_id))
        if record is None:
            return None
        try:
            return cls.from_dict(record)
        except ValueError as exc:
            print(f"ERROR reading customer {customer_id}: {exc}")
            return None

    @classmethod
    def get_all(cls):
        """Return list of all valid Customer instances."""
        data = cls._load_all()
        customers = []
        for cid, record in data.items():
            try:
                customers.append(cls.from_dict(record))
            except ValueError as exc:
                print(f"ERROR reading customer {cid}: {exc}. Skipping record.")
        return customers

    @classmethod
    def delete(cls, customer_id):
        """Remove a customer by ID. Returns True if deleted, False if not found."""
        data = cls._load_all()
        customer_id = str(customer_id)
        if customer_id not in data:
            return False
        del data[customer_id]
        cls._save_all(data)
        return True

    @classmethod
    def modify(cls, customer_id, **kwargs):
        """Update allowed fields for a customer. Returns updated Customer or None."""
        allowed = {"first_name", "last_name", "email", "phone"}
        data = cls._load_all()
        customer_id = str(customer_id)
        if customer_id not in data:
            return None
        record = data[customer_id]
        for key, value in kwargs.items():
            if key in allowed:
                record[key] = value
        try:
            customer = cls.from_dict(record)
        except ValueError as exc:
            print(f"ERROR modifying customer {customer_id}: {exc}")
            return None
        data[customer_id] = customer.to_dict()
        cls._save_all(data)
        return customer
