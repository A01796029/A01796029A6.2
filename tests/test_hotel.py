import sys
import os
import tempfile
import unittest
from unittest.mock import patch
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from models import Hotel
import models

def _patch_data_dir(tmp_dir):
    """Return a dict of patches to redirect all data files to tmp_dir."""
    return {
        "models.data_handler.HOTELS_FILE": os.path.join(tmp_dir, "hotels.json"),
        "models.data_handler.CUSTOMERS_FILE": os.path.join(tmp_dir, "customers.json"),
        "models.data_handler.RESERVATIONS_FILE": os.path.join(tmp_dir, "reservations.json"),
        "models.data_handler.DATA_DIR": tmp_dir,
    }

class TestHotel(unittest.TestCase):
    """Test Hotel create / read / update / delete operations."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.patches = _patch_data_dir(self.tmp)
        self.patchers = [
            patch(target, new_val) for target, new_val in self.patches.items()
        ]
        for p in self.patchers:
            p.start()

    def tearDown(self):
        for p in self.patchers:
            p.stop()

    def test_create_hotel(self):
        hotel = Hotel.create("Grand Inn", "123 Main St", 50, "555-0000")
        self.assertIsInstance(hotel, Hotel)
        self.assertEqual(hotel.name, "Grand Inn")
        self.assertEqual(hotel.total_rooms, 50)

    def test_get_hotel(self):
        hotel = Hotel.create("Sea View", "1 Beach Rd", 20)
        fetched = Hotel.get(hotel.hotel_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.name, "Sea View")

    def test_get_hotel_not_found(self):
        result = Hotel.get("nonexistent-id")
        self.assertIsNone(result)

    def test_get_all_hotels(self):
        Hotel.create("Hotel A", "Addr A", 10)
        Hotel.create("Hotel B", "Addr B", 20)
        hotels = Hotel.get_all()
        self.assertEqual(len(hotels), 2)

    def test_delete_hotel(self):
        hotel = Hotel.create("Delete Me", "Nowhere", 5)
        result = Hotel.delete(hotel.hotel_id)
        self.assertTrue(result)
        self.assertIsNone(Hotel.get(hotel.hotel_id))

    def test_delete_hotel_not_found(self):
        result = Hotel.delete("fake-id")
        self.assertFalse(result)

    def test_modify_hotel(self):
        hotel = Hotel.create("Old Name", "Old Addr", 10)
        updated = Hotel.modify(hotel.hotel_id, name="New Name", total_rooms=15)
        self.assertIsNotNone(updated)
        self.assertEqual(updated.name, "New Name")
        self.assertEqual(updated.total_rooms, 15)

    def test_modify_hotel_not_found(self):
        result = Hotel.modify("fake-id", name="X")
        self.assertIsNone(result)

    def test_hotel_display(self):
        hotel = Hotel.create("Display Hotel", "123 St", 10, "555-1234")
        # Should not raise
        hotel.display()

    def test_hotel_invalid_rooms(self):
        with self.assertRaises(ValueError):
            Hotel("h1", "Bad Hotel", "Addr", -1)

    def test_hotel_invalid_rooms_zero(self):
        with self.assertRaises(ValueError):
            Hotel("h1", "Bad Hotel", "Addr", 0)

    def test_hotel_from_dict_missing_fields(self):
        with self.assertRaises(ValueError):
            Hotel.from_dict({"hotel_id": "1", "name": "X"})

    def test_hotel_to_dict(self):
        hotel = Hotel("h1", "Test", "Addr", 10, "000")
        d = hotel.to_dict()
        self.assertEqual(d["name"], "Test")
        self.assertEqual(d["total_rooms"], 10)

    # def test_get_all_skips_invalid_records(self):
    #     """Invalid records in file should be skipped with error printed."""
    #     hotels_file = os.path.join(self.tmp, "hotels.json")
    #     with open(hotels_file, "w", encoding="utf-8") as fh:
    #         json.dump({"bad-id": {"hotel_id": "bad-id"}}, fh)
    #     with patch("builtins.print"):
    #         hotels = m.Hotel.get_all()
    #     self.assertEqual(len(hotels), 0)

    # def test_load_invalid_json_file(self):
    #     """Corrupt JSON file should return empty dict with error message."""
    #     hotels_file = os.path.join(self.tmp, "hotels.json")
    #     with open(hotels_file, "w", encoding="utf-8") as fh:
    #         fh.write("NOT VALID JSON {{{{")
    #     with patch("builtins.print") as mock_print:
    #         data = m._load_json(hotels_file)
    #     self.assertEqual(data, {})
    #     mock_print.assert_called()

    # def test_load_non_dict_json(self):
    #     """JSON file with list root should return empty dict with error."""
    #     hotels_file = os.path.join(self.tmp, "hotels.json")
    #     with open(hotels_file, "w", encoding="utf-8") as fh:
    #         json.dump([1, 2, 3], fh)
    #     with patch("builtins.print") as mock_print:
    #         data = m._load_json(hotels_file)
    #     self.assertEqual(data, {})
    #     mock_print.assert_called()

    # def test_get_hotel_with_corrupt_record(self):
    #     """Getting a hotel with corrupt record should print error and return None."""
    #     hotels_file = os.path.join(self.tmp, "hotels.json")
    #     with open(hotels_file, "w", encoding="utf-8") as fh:
    #         json.dump({"bad-id": {"name": "Broken"}}, fh)
    #     with patch("builtins.print"):
    #         result = m.Hotel.get("bad-id")
    #     self.assertIsNone(result)

    # def test_modify_hotel_invalid_total_rooms(self):
    #     """Modifying hotel to invalid rooms should print error and return None."""
    #     hotel = m.Hotel.create("Valid Hotel", "Addr", 10)
    #     # Manually corrupt the stored record
    #     hotels_file = os.path.join(self.tmp, "hotels.json")
    #     data = m._load_json(hotels_file)
    #     data[hotel.hotel_id]["total_rooms"] = -5
    #     m._save_json(hotels_file, data)
    #     with patch("builtins.print"):
    #         result = m.Hotel.modify(hotel.hotel_id, name="Still Valid")
    #     self.assertIsNone(result)
