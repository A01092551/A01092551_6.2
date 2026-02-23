"""Unit tests para hotel reservation.

"""
import unittest
from pathlib import Path
from unittest.mock import patch
from hotel_reservation import Hotel, Customer, Reservation


class TestHotel(unittest.TestCase):
    """Test cases for Hotel class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = Path("Results")
        self.hotels_file = self.test_dir / "Hotels.json"
        # Clean up test files before each test
        if self.hotels_file.exists():
            self.hotels_file.unlink()

    def tearDown(self):
        """Clean up test files after each test method."""
        if self.hotels_file.exists():
            self.hotels_file.unlink()

    def test_hotel_create_success(self):
        """Test successful hotel creation."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        result = hotel.create()
        self.assertTrue(result)
        self.assertIsNotNone(hotel.id)
        self.assertEqual(hotel.nombre, "Test Hotel")
        self.assertEqual(hotel.estado, "Test State")
        self.assertEqual(hotel.habitaciones, 50)
        self.assertEqual(hotel.habitaciones_disponibles, 50)

    def test_hotel_create_multiple(self):
        """Test creating multiple hotels with auto-incrementing IDs."""
        hotel1 = Hotel("Hotel 1", "State 1", 100)
        hotel2 = Hotel("Hotel 2", "State 2", 200)
        hotel1.create()
        hotel2.create()
        self.assertEqual(hotel2.id, hotel1.id + 1)

    def test_hotel_delete_success(self):
        """Test successful hotel deletion."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        hotel.create()
        result = hotel.delete()
        self.assertTrue(result)

    def test_hotel_delete_nonexistent(self):
        """Test deleting a non-existent hotel."""
        hotel = Hotel("Test Hotel", "Test State", 50, hotel_id=9999)
        result = hotel.delete()
        self.assertFalse(result)

    def test_hotel_display_info_success(self):
        """Test displaying hotel information."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        hotel.create()
        info = hotel.display_info()
        self.assertIsInstance(info, dict)
        self.assertEqual(info['nombre'], "Test Hotel")
        self.assertEqual(info['estado'], "Test State")
        self.assertEqual(info['habitaciones'], 50)

    def test_hotel_display_info_nonexistent(self):
        """Test displaying info for non-existent hotel."""
        hotel = Hotel("Test Hotel", "Test State", 50, hotel_id=9999)
        info = hotel.display_info()
        self.assertEqual(info, {})

    def test_hotel_modify_info_success(self):
        """Test successful hotel information modification."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        hotel.create()
        result = hotel.modify_info(
            nombre="Modified Hotel",
            estado="Modified State",
            habitaciones=100)
        self.assertTrue(result)
        self.assertEqual(hotel.nombre, "Modified Hotel")
        self.assertEqual(hotel.estado, "Modified State")
        self.assertEqual(hotel.habitaciones, 100)

    def test_hotel_modify_info_partial(self):
        """Test partial modification of hotel information."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        hotel.create()
        result = hotel.modify_info(nombre="New Name")
        self.assertTrue(result)
        self.assertEqual(hotel.nombre, "New Name")
        self.assertEqual(hotel.estado, "Test State")

    def test_hotel_modify_info_nonexistent(self):
        """Test modifying non-existent hotel."""
        hotel = Hotel("Test Hotel", "Test State", 50, hotel_id=9999)
        result = hotel.modify_info(nombre="Modified")
        self.assertFalse(result)

    def test_hotel_reserve_room_success(self):
        """Test successful room reservation."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        hotel.create()
        result = hotel.reserve_room(customer_id=1)
        self.assertTrue(result)
        self.assertEqual(hotel.habitaciones_disponibles, 49)

    def test_hotel_reserve_room_no_availability(self):
        """Test room reservation when no rooms available."""
        hotel = Hotel("Test Hotel", "Test State", 0)
        hotel.create()
        result = hotel.reserve_room(customer_id=1)
        self.assertFalse(result)

    def test_hotel_reserve_room_nonexistent(self):
        """Test reserving room in non-existent hotel."""
        hotel = Hotel("Test Hotel", "Test State", 50, hotel_id=9999)
        result = hotel.reserve_room(customer_id=1)
        self.assertFalse(result)

    def test_hotel_cancel_reservation_success(self):
        """Test successful reservation cancellation."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        hotel.create()
        hotel.reserve_room(customer_id=1)
        initial_available = hotel.habitaciones_disponibles
        result = hotel.cancel_reservation(customer_id=1)
        self.assertTrue(result)
        self.assertEqual(hotel.habitaciones_disponibles, initial_available + 1)

    def test_hotel_cancel_reservation_no_reservations(self):
        """Test canceling reservation when none exist."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        hotel.create()
        result = hotel.cancel_reservation(customer_id=1)
        self.assertFalse(result)

    def test_hotel_cancel_reservation_nonexistent(self):
        """Test canceling reservation in non-existent hotel."""
        hotel = Hotel("Test Hotel", "Test State", 50, hotel_id=9999)
        result = hotel.cancel_reservation(customer_id=1)
        self.assertFalse(result)

    def test_hotel_load_json_file_not_exists(self):
        """Test loading non-existent JSON file."""
        success, data = Hotel._load_json_file(
            Path("nonexistent.json"), "Test")
        self.assertFalse(success)
        self.assertEqual(data, [])

    def test_hotel_load_json_file_empty(self):
        """Test loading empty JSON file."""
        empty_file = self.test_dir / "empty.json"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        empty_file.write_text("")
        success, data = Hotel._load_json_file(empty_file, "Test")
        self.assertFalse(success)
        self.assertEqual(data, [])
        empty_file.unlink()

    def test_hotel_load_json_file_invalid_json(self):
        """Test loading invalid JSON file."""
        invalid_file = self.test_dir / "invalid.json"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        invalid_file.write_text("{invalid json")
        success, data = Hotel._load_json_file(invalid_file, "Test")
        self.assertFalse(success)
        self.assertEqual(data, [])
        invalid_file.unlink()

    def test_hotel_load_json_file_invalid_format(self):
        """Test loading JSON file with invalid format (not a list)."""
        invalid_file = self.test_dir / "invalid_format.json"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        invalid_file.write_text('{"key": "value"}')
        success, data = Hotel._load_json_file(invalid_file, "Test")
        self.assertFalse(success)
        self.assertEqual(data, [])
        invalid_file.unlink()

    def test_hotel_create_with_invalid_existing_data(self):
        """Test hotel creation with corrupted existing data."""
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.hotels_file.write_text('{"invalid": "data"}')
        hotel = Hotel("Test Hotel", "Test State", 50)
        result = hotel.create()
        self.assertTrue(result)
        self.assertEqual(hotel.id, 1)

    def test_hotel_create_io_error(self):
        """Test hotel creation with IO error."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        with patch('builtins.open', side_effect=IOError("Disk full")):
            result = hotel.create()
            self.assertFalse(result)


class TestCustomer(unittest.TestCase):
    """Test cases for Customer class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = Path("Results")
        self.customers_file = self.test_dir / "Customers.json"
        if self.customers_file.exists():
            self.customers_file.unlink()

    def tearDown(self):
        """Clean up test files after each test method."""
        if self.customers_file.exists():
            self.customers_file.unlink()

    def test_customer_create_success(self):
        """Test successful customer creation."""
        customer = Customer("John Doe", "john@email.com", "1234567890")
        result = customer.create()
        self.assertTrue(result)
        self.assertIsNotNone(customer.id)
        self.assertEqual(customer.nombre, "John Doe")
        self.assertEqual(customer.email, "john@email.com")
        self.assertEqual(customer.telefono, "1234567890")

    def test_customer_create_multiple(self):
        """Test creating multiple customers with auto-incrementing IDs."""
        customer1 = Customer("Customer 1", "c1@email.com", "1111111111")
        customer2 = Customer("Customer 2", "c2@email.com", "2222222222")
        customer1.create()
        customer2.create()
        self.assertEqual(customer2.id, customer1.id + 1)

    def test_customer_delete_success(self):
        """Test successful customer deletion."""
        customer = Customer("John Doe", "john@email.com", "1234567890")
        customer.create()
        result = customer.delete()
        self.assertTrue(result)

    def test_customer_delete_nonexistent(self):
        """Test deleting a non-existent customer."""
        customer = Customer("John Doe", "john@email.com", "1234567890",
                            customer_id=9999)
        result = customer.delete()
        self.assertFalse(result)

    def test_customer_display_info_success(self):
        """Test displaying customer information."""
        customer = Customer("John Doe", "john@email.com", "1234567890")
        customer.create()
        info = customer.display_info()
        self.assertIsInstance(info, dict)
        self.assertEqual(info['nombre'], "John Doe")
        self.assertEqual(info['email'], "john@email.com")
        self.assertEqual(info['telefono'], "1234567890")

    def test_customer_display_info_nonexistent(self):
        """Test displaying info for non-existent customer."""
        customer = Customer("John Doe", "john@email.com", "1234567890",
                            customer_id=9999)
        info = customer.display_info()
        self.assertEqual(info, {})

    def test_customer_modify_info_success(self):
        """Test successful customer information modification."""
        customer = Customer("John Doe", "john@email.com", "1234567890")
        customer.create()
        result = customer.modify_info(
            nombre="Jane Doe",
            email="jane@email.com",
            telefono="0987654321")
        self.assertTrue(result)
        self.assertEqual(customer.nombre, "Jane Doe")
        self.assertEqual(customer.email, "jane@email.com")
        self.assertEqual(customer.telefono, "0987654321")

    def test_customer_modify_info_partial(self):
        """Test partial modification of customer information."""
        customer = Customer("John Doe", "john@email.com", "1234567890")
        customer.create()
        result = customer.modify_info(email="newemail@email.com")
        self.assertTrue(result)
        self.assertEqual(customer.email, "newemail@email.com")
        self.assertEqual(customer.nombre, "John Doe")

    def test_customer_modify_info_nonexistent(self):
        """Test modifying non-existent customer."""
        customer = Customer("John Doe", "john@email.com", "1234567890",
                            customer_id=9999)
        result = customer.modify_info(nombre="Modified")
        self.assertFalse(result)

    def test_customer_load_json_file_not_exists(self):
        """Test loading non-existent JSON file."""
        success, data = Customer._load_json_file(
            Path("nonexistent.json"), "Test")
        self.assertFalse(success)
        self.assertEqual(data, [])

    def test_customer_load_json_file_empty(self):
        """Test loading empty JSON file."""
        empty_file = self.test_dir / "empty_customer.json"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        empty_file.write_text("")
        success, data = Customer._load_json_file(empty_file, "Test")
        self.assertFalse(success)
        self.assertEqual(data, [])
        empty_file.unlink()

    def test_customer_load_json_file_invalid_json(self):
        """Test loading invalid JSON file."""
        invalid_file = self.test_dir / "invalid_customer.json"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        invalid_file.write_text("{invalid json")
        success, data = Customer._load_json_file(invalid_file, "Test")
        self.assertFalse(success)
        self.assertEqual(data, [])
        invalid_file.unlink()

    def test_customer_load_json_file_invalid_format(self):
        """Test loading JSON file with invalid format (not a list)."""
        invalid_file = self.test_dir / "invalid_format_customer.json"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        invalid_file.write_text('{"key": "value"}')
        success, data = Customer._load_json_file(invalid_file, "Test")
        self.assertFalse(success)
        self.assertEqual(data, [])
        invalid_file.unlink()

    def test_customer_create_with_invalid_existing_data(self):
        """Test customer creation with corrupted existing data."""
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.customers_file.write_text('[{"invalid": "data"}]')
        customer = Customer("John Doe", "john@email.com", "1234567890")
        result = customer.create()
        self.assertTrue(result)

    def test_customer_create_io_error(self):
        """Test customer creation with IO error."""
        customer = Customer("John Doe", "john@email.com", "1234567890")
        with patch('builtins.open', side_effect=IOError("Disk full")):
            result = customer.create()
            self.assertFalse(result)


class TestReservation(unittest.TestCase):
    """Test cases for Reservation class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = Path("Results")
        self.reservations_file = self.test_dir / "Reservations.json"
        self.hotels_file = self.test_dir / "Hotels.json"
        self.customers_file = self.test_dir / "Customers.json"

        # Clean up test files
        for file in [self.reservations_file, self.hotels_file,
                     self.customers_file]:
            if file.exists():
                file.unlink()

        # Create test hotel and customer
        self.hotel = Hotel("Test Hotel", "Test State", 50)
        self.hotel.create()
        self.customer = Customer("John Doe", "john@email.com", "1234567890")
        self.customer.create()

    def tearDown(self):
        """Clean up test files after each test method."""
        for file in [self.reservations_file, self.hotels_file,
                     self.customers_file]:
            if file.exists():
                file.unlink()

    def test_reservation_create_success(self):
        """Test successful reservation creation."""
        reservation = Reservation(self.customer.id, self.hotel.id)
        result = reservation.create()
        self.assertTrue(result)
        self.assertIsNotNone(reservation.id)
        self.assertEqual(reservation.customer_id, self.customer.id)
        self.assertEqual(reservation.hotel_id, self.hotel.id)

    def test_reservation_create_multiple(self):
        """Test creating multiple reservations with auto-incrementing IDs."""
        reservation1 = Reservation(self.customer.id, self.hotel.id)
        reservation2 = Reservation(self.customer.id, self.hotel.id)
        reservation1.create()
        reservation2.create()
        self.assertEqual(reservation2.id, reservation1.id + 1)

    def test_reservation_create_nonexistent_customer(self):
        """Test creating reservation with non-existent customer."""
        reservation = Reservation(9999, self.hotel.id)
        result = reservation.create()
        self.assertFalse(result)

    def test_reservation_create_nonexistent_hotel(self):
        """Test creating reservation with non-existent hotel."""
        reservation = Reservation(self.customer.id, 9999)
        result = reservation.create()
        self.assertFalse(result)

    def test_reservation_create_no_rooms_available(self):
        """Test creating reservation when no rooms available."""
        hotel_full = Hotel("Full Hotel", "Test State", 0)
        hotel_full.create()
        reservation = Reservation(self.customer.id, hotel_full.id)
        result = reservation.create()
        self.assertFalse(result)

    def test_reservation_cancel_success(self):
        """Test successful reservation cancellation."""
        reservation = Reservation(self.customer.id, self.hotel.id)
        reservation.create()
        result = reservation.cancel()
        self.assertTrue(result)

    def test_reservation_cancel_nonexistent(self):
        """Test canceling non-existent reservation."""
        reservation = Reservation(
            self.customer.id, self.hotel.id, reservation_id=9999)
        result = reservation.cancel()
        self.assertFalse(result)

    def test_reservation_cancel_file_not_exists(self):
        """Test canceling reservation when file doesn't exist."""
        reservation = Reservation(
            self.customer.id, self.hotel.id, reservation_id=1)
        if self.reservations_file.exists():
            self.reservations_file.unlink()
        result = reservation.cancel()
        self.assertFalse(result)

    def test_reservation_load_json_file_not_exists(self):
        """Test loading non-existent JSON file."""
        success, data = Reservation._load_json_file(
            Path("nonexistent.json"), "Test")
        self.assertFalse(success)
        self.assertEqual(data, [])

    def test_reservation_load_json_file_empty(self):
        """Test loading empty JSON file."""
        empty_file = self.test_dir / "empty_reservation.json"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        empty_file.write_text("")
        success, data = Reservation._load_json_file(empty_file, "Test")
        self.assertFalse(success)
        self.assertEqual(data, [])
        empty_file.unlink()

    def test_reservation_load_json_file_invalid_json(self):
        """Test loading invalid JSON file."""
        invalid_file = self.test_dir / "invalid_reservation.json"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        invalid_file.write_text("{invalid json")
        success, data = Reservation._load_json_file(invalid_file, "Test")
        self.assertFalse(success)
        self.assertEqual(data, [])
        invalid_file.unlink()

    def test_reservation_load_json_file_invalid_format(self):
        """Test loading JSON file with invalid format (not a list)."""
        invalid_file = self.test_dir / "invalid_format_reservation.json"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        invalid_file.write_text('{"key": "value"}')
        success, data = Reservation._load_json_file(invalid_file, "Test")
        self.assertFalse(success)
        self.assertEqual(data, [])
        invalid_file.unlink()

    def test_reservation_create_with_invalid_existing_data(self):
        """Test reservation creation with corrupted existing data."""
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.reservations_file.write_text('{"invalid": "data"}')
        reservation = Reservation(self.customer.id, self.hotel.id)
        result = reservation.create()
        self.assertTrue(result)

    def test_reservation_create_io_error(self):
        """Test reservation creation with IO error."""
        reservation = Reservation(self.customer.id, self.hotel.id)
        with patch('pathlib.Path.mkdir'):
            with patch('builtins.open', side_effect=IOError("Disk full")):
                result = reservation.create()
                self.assertFalse(result)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete reservation system."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = Path("Results")
        self.reservations_file = self.test_dir / "Reservations.json"
        self.hotels_file = self.test_dir / "Hotels.json"
        self.customers_file = self.test_dir / "Customers.json"

        for file in [self.reservations_file, self.hotels_file,
                     self.customers_file]:
            if file.exists():
                file.unlink()

    def tearDown(self):
        """Clean up test files after each test method."""
        for file in [self.reservations_file, self.hotels_file,
                     self.customers_file]:
            if file.exists():
                file.unlink()

    def test_complete_reservation_workflow(self):
        """Test complete workflow: create hotel, customer, reservation."""
        # Create hotel
        hotel = Hotel("Integration Hotel", "Test State", 100)
        self.assertTrue(hotel.create())

        # Create customer
        customer = Customer("Test User", "test@email.com", "5555555555")
        self.assertTrue(customer.create())

        # Create reservation
        reservation = Reservation(customer.id, hotel.id)
        self.assertTrue(reservation.create())

        # Verify room was reserved
        hotel_info = hotel.display_info()
        self.assertEqual(hotel_info['habitaciones_disponibles'], 99)

        # Cancel reservation
        self.assertTrue(reservation.cancel())

        # Verify room was freed
        hotel_info = hotel.display_info()
        self.assertEqual(hotel_info['habitaciones_disponibles'], 100)

    def test_modify_and_delete_workflow(self):
        """Test modification and deletion workflow."""
        # Create entities
        hotel = Hotel("Original Hotel", "Original State", 50)
        hotel.create()
        customer = Customer("Original Name", "original@email.com",
                            "1111111111")
        customer.create()

        # Modify hotel
        hotel.modify_info(nombre="Modified Hotel", habitaciones=75)
        hotel_info = hotel.display_info()
        self.assertEqual(hotel_info['nombre'], "Modified Hotel")
        self.assertEqual(hotel_info['habitaciones'], 75)

        # Modify customer
        customer.modify_info(email="modified@email.com")
        customer_info = customer.display_info()
        self.assertEqual(customer_info['email'], "modified@email.com")

        # Delete entities
        self.assertTrue(customer.delete())
        self.assertTrue(hotel.delete())

        # Verify deletion
        self.assertEqual(customer.display_info(), {})
        self.assertEqual(hotel.display_info(), {})

    def test_multiple_reservations_workflow(self):
        """Test multiple reservations on same hotel."""
        # Create hotel with limited rooms
        hotel = Hotel("Small Hotel", "Test State", 2)
        hotel.create()

        # Create customers
        customer1 = Customer("Customer 1", "c1@email.com", "1111111111")
        customer2 = Customer("Customer 2", "c2@email.com", "2222222222")
        customer3 = Customer("Customer 3", "c3@email.com", "3333333333")
        customer1.create()
        customer2.create()
        customer3.create()

        # Create two reservations
        reservation1 = Reservation(customer1.id, hotel.id)
        reservation2 = Reservation(customer2.id, hotel.id)
        self.assertTrue(reservation1.create())
        self.assertTrue(reservation2.create())

        # Verify no rooms available
        hotel_info = hotel.display_info()
        self.assertEqual(hotel_info['habitaciones_disponibles'], 0)

        # Try to create third reservation (should fail)
        reservation3 = Reservation(customer3.id, hotel.id)
        self.assertFalse(reservation3.create())

        # Cancel one reservation
        self.assertTrue(reservation1.cancel())

        # Verify room is available again
        hotel_info = hotel.display_info()
        self.assertEqual(hotel_info['habitaciones_disponibles'], 1)


if __name__ == '__main__':
    unittest.main()
