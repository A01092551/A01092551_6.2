"""Pruebas unitarias para hotel_reservation.py."""

import unittest
from pathlib import Path
from unittest.mock import patch
from hotel_reservation import Hotel, Customer, Reservation


class TestHotel(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """Casos de prueba para la clase Hotel."""

    def setUp(self):
        """Configura los datos antes de cada prueba."""
        self.test_dir = Path("Results")
        self.hotels_file = self.test_dir / "Hotels.json"
        # Limpia archivos de prueba antes de cada prueba
        if self.hotels_file.exists():
            self.hotels_file.unlink()

    def tearDown(self):
        """Limpia archivos de prueba despues de cada prueba."""
        if self.hotels_file.exists():
            self.hotels_file.unlink()

    def test_hotel_create_success(self):
        """Prueba la creacion exitosa de un hotel."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        result = hotel.create()
        self.assertTrue(result)
        self.assertIsNotNone(hotel.id)
        self.assertEqual(hotel.nombre, "Test Hotel")
        self.assertEqual(hotel.estado, "Test State")
        self.assertEqual(hotel.habitaciones, 50)
        self.assertEqual(hotel.habitaciones_disponibles, 50)

    def test_hotel_create_multiple(self):
        """Prueba crear varios hoteles con IDs autoincrementales."""
        hotel1 = Hotel("Hotel 1", "State 1", 100)
        hotel2 = Hotel("Hotel 2", "State 2", 200)
        hotel1.create()
        hotel2.create()
        self.assertEqual(hotel2.id, hotel1.id + 1)

    def test_hotel_delete_success(self):
        """Prueba la eliminacion exitosa de un hotel."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        hotel.create()
        result = hotel.delete()
        self.assertTrue(result)

    def test_hotel_delete_nonexistent(self):
        """Prueba eliminar un hotel inexistente."""
        hotel = Hotel("Test Hotel", "Test State", 50, hotel_id=9999)
        result = hotel.delete()
        self.assertFalse(result)

    def test_hotel_display_info_success(self):
        """Prueba mostrar la informacion de un hotel."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        hotel.create()
        info = hotel.display_info()
        self.assertIsInstance(info, dict)
        self.assertEqual(info['nombre'], "Test Hotel")
        self.assertEqual(info['estado'], "Test State")
        self.assertEqual(info['habitaciones'], 50)

    def test_hotel_display_info_nonexistent(self):
        """Prueba mostrar informacion de un hotel inexistente."""
        hotel = Hotel("Test Hotel", "Test State", 50, hotel_id=9999)
        info = hotel.display_info()
        self.assertEqual(info, {})

    def test_hotel_modify_info_success(self):
        """Prueba modificar exitosamente la informacion de un hotel."""
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
        """Prueba la modificacion parcial de informacion del hotel."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        hotel.create()
        result = hotel.modify_info(nombre="New Name")
        self.assertTrue(result)
        self.assertEqual(hotel.nombre, "New Name")
        self.assertEqual(hotel.estado, "Test State")

    def test_hotel_modify_info_nonexistent(self):
        """Prueba modificar un hotel inexistente."""
        hotel = Hotel("Test Hotel", "Test State", 50, hotel_id=9999)
        result = hotel.modify_info(nombre="Modified")
        self.assertFalse(result)

    def test_hotel_reserve_room_success(self):
        """Prueba la reservacion exitosa de una habitacion."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        hotel.create()
        result = hotel.reserve_room(customer_id=1)
        self.assertTrue(result)
        self.assertEqual(hotel.habitaciones_disponibles, 49)

    def test_hotel_reserve_room_no_availability(self):
        """Prueba reservar cuando no hay habitaciones disponibles."""
        hotel = Hotel("Test Hotel", "Test State", 0)
        hotel.create()
        result = hotel.reserve_room(customer_id=1)
        self.assertFalse(result)

    def test_hotel_reserve_room_nonexistent(self):
        """Prueba reservar en un hotel inexistente."""
        hotel = Hotel("Test Hotel", "Test State", 50, hotel_id=9999)
        result = hotel.reserve_room(customer_id=1)
        self.assertFalse(result)

    def test_hotel_cancel_reservation_success(self):
        """Prueba cancelar exitosamente una reservacion."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        hotel.create()
        hotel.reserve_room(customer_id=1)
        initial_available = hotel.habitaciones_disponibles
        result = hotel.cancel_reservation(customer_id=1)
        self.assertTrue(result)
        self.assertEqual(hotel.habitaciones_disponibles, initial_available + 1)

    def test_hotel_cancel_reservation_no_reservations(self):
        """Prueba cancelar una reservacion cuando no existe ninguna."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        hotel.create()
        result = hotel.cancel_reservation(customer_id=1)
        self.assertFalse(result)

    def test_hotel_cancel_reservation_nonexistent(self):
        """Prueba cancelar reservacion en un hotel inexistente."""
        hotel = Hotel("Test Hotel", "Test State", 50, hotel_id=9999)
        result = hotel.cancel_reservation(customer_id=1)
        self.assertFalse(result)

    def test_hotel_create_io_error(self):
        """Prueba crear hotel cuando ocurre un error de IO."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        with patch('builtins.open', side_effect=IOError("Disk full")):
            result = hotel.create()
            self.assertFalse(result)

    def test_hotel_delete_io_error(self):
        """Prueba eliminar hotel con error de IO durante escritura."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        hotel.create()
        original_open = open

        def selective_open(*args, **kwargs):
            if 'w' in args[1] if len(args) > 1 else kwargs.get('mode', 'r'):
                raise IOError("Disk full")
            return original_open(*args, **kwargs)
        with patch('builtins.open', side_effect=selective_open):
            result = hotel.delete()
            self.assertFalse(result)

    def test_hotel_modify_info_io_error(self):
        """Prueba modificar hotel con error de IO durante escritura."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        hotel.create()
        original_open = open

        def selective_open(*args, **kwargs):
            if 'w' in args[1] if len(args) > 1 else kwargs.get('mode', 'r'):
                raise IOError("Disk full")
            return original_open(*args, **kwargs)
        with patch('builtins.open', side_effect=selective_open):
            result = hotel.modify_info(nombre="New Name")
            self.assertFalse(result)

    def test_hotel_reserve_room_io_error(self):
        """Prueba reserve_room con error de IO durante escritura."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        hotel.create()
        original_open = open

        def selective_open(*args, **kwargs):
            if 'w' in args[1] if len(args) > 1 else kwargs.get('mode', 'r'):
                raise IOError("Disk full")
            return original_open(*args, **kwargs)
        with patch('builtins.open', side_effect=selective_open):
            result = hotel.reserve_room(customer_id=1)
            self.assertFalse(result)

    def test_hotel_cancel_reservation_io_error(self):
        """Prueba cancel_reservation con error de IO durante escritura."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        hotel.create()
        original_open = open

        def selective_open(*args, **kwargs):
            if 'w' in args[1] if len(args) > 1 else kwargs.get('mode', 'r'):
                raise IOError("Disk full")
            return original_open(*args, **kwargs)
        with patch('builtins.open', side_effect=selective_open):
            result = hotel.cancel_reservation(customer_id=1)
            self.assertFalse(result)

    def test_hotel_delete_not_found_in_file(self):
        """Prueba eliminar hotel que existe en memoria pero no en archivo."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        hotel.create()
        hotel.id = 9999
        result = hotel.delete()
        self.assertFalse(result)

    def test_hotel_modify_info_not_found_in_file(self):
        """Prueba modificar hotel que existe en memoria pero no en archivo."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        hotel.create()
        hotel.id = 9999
        result = hotel.modify_info(nombre="New Name")
        self.assertFalse(result)

    def test_hotel_reserve_room_not_found_in_file(self):
        """Prueba reservar en hotel que existe en memoria pero no en archivo."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        hotel.create()
        hotel.id = 9999
        result = hotel.reserve_room(customer_id=1)
        self.assertFalse(result)

    def test_hotel_cancel_reservation_not_found_in_file(self):
        """Prueba cancelar reservacion en hotel existente solo en memoria."""
        hotel = Hotel("Test Hotel", "Test State", 50)
        hotel.create()
        hotel.id = 9999
        result = hotel.cancel_reservation(customer_id=1)
        self.assertFalse(result)


class TestCustomer(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """Casos de prueba para la clase Customer."""

    def setUp(self):
        """Configura los datos antes de cada prueba."""
        self.test_dir = Path("Results")
        self.customers_file = self.test_dir / "Customers.json"
        if self.customers_file.exists():
            self.customers_file.unlink()

    def tearDown(self):
        """Limpia archivos de prueba despues de cada prueba."""
        if self.customers_file.exists():
            self.customers_file.unlink()

    def test_customer_create_success(self):
        """Prueba la creacion exitosa de un cliente."""
        customer = Customer("John Doe", "john@email.com", "1234567890")
        result = customer.create()
        self.assertTrue(result)
        self.assertIsNotNone(customer.id)
        self.assertEqual(customer.nombre, "John Doe")
        self.assertEqual(customer.email, "john@email.com")
        self.assertEqual(customer.telefono, "1234567890")

    def test_customer_create_multiple(self):
        """Prueba crear varios clientes con IDs autoincrementales."""
        customer1 = Customer("Customer 1", "c1@email.com", "1111111111")
        customer2 = Customer("Customer 2", "c2@email.com", "2222222222")
        customer1.create()
        customer2.create()
        self.assertEqual(customer2.id, customer1.id + 1)

    def test_customer_delete_success(self):
        """Prueba la eliminacion exitosa de un cliente."""
        customer = Customer("John Doe", "john@email.com", "1234567890")
        customer.create()
        result = customer.delete()
        self.assertTrue(result)

    def test_customer_delete_nonexistent(self):
        """Prueba eliminar un cliente inexistente."""
        customer = Customer("John Doe", "john@email.com", "1234567890",
                            customer_id=9999)
        result = customer.delete()
        self.assertFalse(result)

    def test_customer_display_info_success(self):
        """Prueba mostrar la informacion del cliente."""
        customer = Customer("John Doe", "john@email.com", "1234567890")
        customer.create()
        info = customer.display_info()
        self.assertIsInstance(info, dict)
        self.assertEqual(info['nombre'], "John Doe")
        self.assertEqual(info['email'], "john@email.com")
        self.assertEqual(info['telefono'], "1234567890")

    def test_customer_display_info_nonexistent(self):
        """Prueba mostrar informacion de cliente inexistente."""
        customer = Customer("John Doe", "john@email.com", "1234567890",
                            customer_id=9999)
        info = customer.display_info()
        self.assertEqual(info, {})

    def test_customer_modify_info_success(self):
        """Prueba modificar exitosamente la informacion del cliente."""
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
        """Prueba la modificacion parcial de informacion del cliente."""
        customer = Customer("John Doe", "john@email.com", "1234567890")
        customer.create()
        result = customer.modify_info(email="newemail@email.com")
        self.assertTrue(result)
        self.assertEqual(customer.email, "newemail@email.com")
        self.assertEqual(customer.nombre, "John Doe")

    def test_customer_modify_info_nonexistent(self):
        """Prueba modificar un cliente inexistente."""
        customer = Customer("John Doe", "john@email.com", "1234567890",
                            customer_id=9999)
        result = customer.modify_info(nombre="Modified")
        self.assertFalse(result)

    def test_customer_create_io_error(self):
        """Prueba crear cliente cuando ocurre un error de IO."""
        customer = Customer("John Doe", "john@email.com", "1234567890")
        with patch('builtins.open', side_effect=IOError("Disk full")):
            result = customer.create()
            self.assertFalse(result)

    def test_customer_delete_io_error(self):
        """Prueba eliminar cliente con error de IO durante escritura."""
        customer = Customer("John Doe", "john@email.com", "1234567890")
        customer.create()
        original_open = open

        def selective_open(*args, **kwargs):
            if 'w' in args[1] if len(args) > 1 else kwargs.get('mode', 'r'):
                raise IOError("Disk full")
            return original_open(*args, **kwargs)
        with patch('builtins.open', side_effect=selective_open):
            result = customer.delete()
            self.assertFalse(result)

    def test_customer_modify_info_io_error(self):
        """Prueba modificar cliente con error de IO durante escritura."""
        customer = Customer("John Doe", "john@email.com", "1234567890")
        customer.create()
        original_open = open

        def selective_open(*args, **kwargs):
            if 'w' in args[1] if len(args) > 1 else kwargs.get('mode', 'r'):
                raise IOError("Disk full")
            return original_open(*args, **kwargs)
        with patch('builtins.open', side_effect=selective_open):
            result = customer.modify_info(nombre="New Name")
            self.assertFalse(result)

    def test_customer_delete_not_found_in_file(self):
        """Prueba eliminar cliente que existe en memoria pero no en archivo."""
        customer = Customer("John Doe", "john@email.com", "1234567890")
        customer.create()
        customer.id = 9999
        result = customer.delete()
        self.assertFalse(result)

    def test_customer_modify_info_not_found_in_file(self):
        """Prueba modificar cliente que existe en memoria pero no en archivo."""
        customer = Customer("John Doe", "john@email.com", "1234567890")
        customer.create()
        customer.id = 9999
        result = customer.modify_info(nombre="New Name")
        self.assertFalse(result)


class TestReservation(unittest.TestCase):
    """Casos de prueba para la clase Reservation."""

    def setUp(self):
        """Configura los datos antes de cada prueba."""
        self.test_dir = Path("Results")
        self.reservations_file = self.test_dir / "Reservations.json"
        self.hotels_file = self.test_dir / "Hotels.json"
        self.customers_file = self.test_dir / "Customers.json"

        # Limpia archivos de prueba
        for file in [self.reservations_file, self.hotels_file,
                     self.customers_file]:
            if file.exists():
                file.unlink()

        # Crea hotel y cliente de prueba
        self.hotel = Hotel("Test Hotel", "Test State", 50)
        self.hotel.create()
        self.customer = Customer("John Doe", "john@email.com", "1234567890")
        self.customer.create()

    def tearDown(self):
        """Limpia archivos de prueba despues de cada prueba."""
        for file in [self.reservations_file, self.hotels_file,
                     self.customers_file]:
            if file.exists():
                file.unlink()

    def test_reservation_create_success(self):
        """Prueba la creacion exitosa de una reservacion."""
        reservation = Reservation(self.customer.id, self.hotel.id)
        result = reservation.create()
        self.assertTrue(result)
        self.assertIsNotNone(reservation.id)
        self.assertEqual(reservation.customer_id, self.customer.id)
        self.assertEqual(reservation.hotel_id, self.hotel.id)

    def test_reservation_create_multiple(self):
        """Prueba crear varias reservaciones con IDs autoincrementales."""
        reservation1 = Reservation(self.customer.id, self.hotel.id)
        reservation2 = Reservation(self.customer.id, self.hotel.id)
        reservation1.create()
        reservation2.create()
        self.assertEqual(reservation2.id, reservation1.id + 1)

    def test_reservation_create_nonexistent_customer(self):
        """Prueba crear reservacion con cliente inexistente."""
        reservation = Reservation(9999, self.hotel.id)
        result = reservation.create()
        self.assertFalse(result)

    def test_reservation_create_nonexistent_hotel(self):
        """Prueba crear reservacion con hotel inexistente."""
        reservation = Reservation(self.customer.id, 9999)
        result = reservation.create()
        self.assertFalse(result)

    def test_reservation_create_no_rooms_available(self):
        """Prueba crear reservacion cuando no hay habitaciones."""
        hotel_full = Hotel("Full Hotel", "Test State", 0)
        hotel_full.create()
        reservation = Reservation(self.customer.id, hotel_full.id)
        result = reservation.create()
        self.assertFalse(result)

    def test_reservation_cancel_success(self):
        """Prueba cancelar exitosamente una reservacion."""
        reservation = Reservation(self.customer.id, self.hotel.id)
        reservation.create()
        result = reservation.cancel()
        self.assertTrue(result)

    def test_reservation_cancel_nonexistent(self):
        """Prueba cancelar una reservacion inexistente."""
        reservation = Reservation(
            self.customer.id, self.hotel.id, reservation_id=9999)
        result = reservation.cancel()
        self.assertFalse(result)

    def test_reservation_cancel_not_found_in_file(self):
        """Prueba cancelar reservacion que existe en memoria pero no en archivo."""
        reservation = Reservation(self.customer.id, self.hotel.id)
        reservation.create()
        reservation.id = 9999
        result = reservation.cancel()
        self.assertFalse(result)


class TestIntegration(unittest.TestCase):
    """Pruebas de integracion para el sistema completo de reservaciones."""

    def setUp(self):
        """Configura los datos antes de cada prueba."""
        self.test_dir = Path("Results")
        self.reservations_file = self.test_dir / "Reservations.json"
        self.hotels_file = self.test_dir / "Hotels.json"
        self.customers_file = self.test_dir / "Customers.json"

        for file in [self.reservations_file, self.hotels_file,
                     self.customers_file]:
            if file.exists():
                file.unlink()

    def tearDown(self):
        """Limpia archivos de prueba despues de cada prueba."""
        for file in [self.reservations_file, self.hotels_file,
                     self.customers_file]:
            if file.exists():
                file.unlink()

    def test_complete_reservation_workflow(self):
        """Prueba flujo completo: crear hotel, cliente y reservacion."""
        # Crear hotel
        hotel = Hotel("Integration Hotel", "Test State", 100)
        self.assertTrue(hotel.create())

        # Crear cliente
        customer = Customer("Test User", "test@email.com", "5555555555")
        self.assertTrue(customer.create())

        # Crear reservacion
        reservation = Reservation(customer.id, hotel.id)
        self.assertTrue(reservation.create())

        # Verificar que la habitacion se reservo
        hotel_info = hotel.display_info()
        self.assertEqual(hotel_info['habitaciones_disponibles'], 99)

        # Cancelar reservacion
        self.assertTrue(reservation.cancel())

        # Verificar que la habitacion se libero
        hotel_info = hotel.display_info()
        self.assertEqual(hotel_info['habitaciones_disponibles'], 100)

    def test_modify_and_delete_workflow(self):
        """Prueba flujo de modificacion y eliminacion."""
        # Crear entidades
        hotel = Hotel("Original Hotel", "Original State", 50)
        hotel.create()
        customer = Customer("Original Name", "original@email.com",
                            "1111111111")
        customer.create()

        # Modificar hotel
        hotel.modify_info(nombre="Modified Hotel", habitaciones=75)
        hotel_info = hotel.display_info()
        self.assertEqual(hotel_info['nombre'], "Modified Hotel")
        self.assertEqual(hotel_info['habitaciones'], 75)

        # Modificar cliente
        customer.modify_info(email="modified@email.com")
        customer_info = customer.display_info()
        self.assertEqual(customer_info['email'], "modified@email.com")

        # Eliminar entidades
        self.assertTrue(customer.delete())
        self.assertTrue(hotel.delete())

        # Verificar eliminacion
        self.assertEqual(customer.display_info(), {})
        self.assertEqual(hotel.display_info(), {})

    def test_multiple_reservations_workflow(self):
        """Prueba multiples reservaciones en el mismo hotel."""
        # Crear hotel con habitaciones limitadas
        hotel = Hotel("Small Hotel", "Test State", 2)
        hotel.create()

        # Crear clientes
        customer1 = Customer("Customer 1", "c1@email.com", "1111111111")
        customer2 = Customer("Customer 2", "c2@email.com", "2222222222")
        customer3 = Customer("Customer 3", "c3@email.com", "3333333333")
        customer1.create()
        customer2.create()
        customer3.create()

        # Crear dos reservaciones
        reservation1 = Reservation(customer1.id, hotel.id)
        reservation2 = Reservation(customer2.id, hotel.id)
        self.assertTrue(reservation1.create())
        self.assertTrue(reservation2.create())

        # Verificar que no hay habitaciones disponibles
        hotel_info = hotel.display_info()
        self.assertEqual(hotel_info['habitaciones_disponibles'], 0)

        # Intentar crear una tercera reservacion (debe fallar)
        reservation3 = Reservation(customer3.id, hotel.id)
        self.assertFalse(reservation3.create())

        # Cancelar una reservacion
        self.assertTrue(reservation1.cancel())

        # Verificar que la habitacion vuelve a estar disponible
        hotel_info = hotel.display_info()
        self.assertEqual(hotel_info['habitaciones_disponibles'], 1)


if __name__ == '__main__':
    unittest.main()
