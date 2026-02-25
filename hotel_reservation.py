"""
Sistema de reservación de hoteles.

Este módulo proporciona clases para gestionar hoteles, clientes y
reservaciones.
Guarda las modificaciones en archivos JSON.
"""
from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def load_json_file(
    file_path: Path,
    file_type: str,
) -> tuple[bool, list]:
    """Función para abrir archivos, evita duplicar código."""

    if not file_path.exists():
        logger.error("El archivo %s.json no existe.", file_type)
        return False, []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().strip()

            if not content:
                logger.error("El archivo %s.json está vacío.", file_type)
                return False, []

            data = json.loads(content)

            if not isinstance(data, list):
                logger.error(
                    "Formato inválido en %s.json. Se esperaba una lista.",
                    file_type,
                )
                return False, []

            return True, data

    except json.JSONDecodeError as error:
        logger.error(
            "JSON inválido en %s.json: %s",
            file_type,
            error,
        )
        return False, []

    except IOError as error:
        logger.error(
            "Error de lectura en %s.json: %s",
            file_type,
            error,
        )
        return False, []


class Hotel:
    """Clase para gestionar hoteles."""

    output_dir = Path("Results")

    def __init__(
        self,
        nombre: str,
        estado: str,
        habitaciones: int,
        hotel_id: Optional[int] = None,
    ):
        self.id = hotel_id
        self.nombre = nombre
        self.estado = estado
        self.habitaciones = habitaciones
        self.habitaciones_disponibles = habitaciones

    def create(self) -> bool:
        """Crea un nuevo hotel y lo guarda en Hotels.json."""
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            output_file = self.output_dir / "Hotels.json"

            hotels = []
            if output_file.exists():
                success, hotels = load_json_file(output_file, "Hotels")
                if not success:
                    hotels = []

            new_id = 1
            if hotels:
                try:
                    max_id = max(
                        h.get("id", 0) for h in hotels if isinstance(h, dict)
                    )
                    new_id = max_id + 1
                except (ValueError, TypeError) as error:
                    logger.warning(
                        "Error calculando ID siguiente: %s. Usando ID 1.",
                        error,
                    )

            self.id = new_id

            hotel_data = {
                "id": self.id,
                "nombre": self.nombre,
                "estado": self.estado,
                "habitaciones": self.habitaciones,
                "habitaciones_disponibles": self.habitaciones_disponibles,
            }

            hotels.append(hotel_data)

            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(hotels, file, indent=2, ensure_ascii=False)

            logger.info("Hotel creado: ID %s - %s", self.id, self.nombre)
            return True

        except (IOError, OSError) as error:
            logger.error("Error al escribir archivo: %s", error)
            return False

    def delete(self) -> bool:
        """Elimina el hotel del archivo Hotels.json."""
        output_file = self.output_dir / "Hotels.json"
        success, hotels = load_json_file(output_file, "Hotels")

        if not success:
            return False

        initial_count = len(hotels)
        hotels = [
            h for h in hotels
            if isinstance(h, dict) and h.get("id") != self.id
        ]

        if len(hotels) == initial_count:
            logger.error("No se encontró hotel con ID %s", self.id)
            return False

        try:
            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(hotels, file, indent=2, ensure_ascii=False)

            logger.info("Hotel con ID %s eliminado.", self.id)
            return True

        except (IOError, OSError) as error:
            logger.error("Error al escribir archivo: %s", error)
            return False

    def display_info(self) -> dict[str, Any]:
        """Devuelve la información del hotel."""
        output_file = self.output_dir / "Hotels.json"
        success, hotels = load_json_file(output_file, "Hotels")

        if not success:
            return {}

        for hotel in hotels:
            if isinstance(hotel, dict) and hotel.get("id") == self.id:
                logger.info("Hotel encontrado: %s", hotel)
                return hotel

        logger.error("No se encontró hotel con ID %s", self.id)
        return {}

    def modify_info(
        self,
        nombre: Optional[str] = None,
        estado: Optional[str] = None,
        habitaciones: Optional[int] = None,
    ) -> bool:
        """Modifica la información del hotel."""
        output_file = self.output_dir / "Hotels.json"
        success, hotels = load_json_file(output_file, "Hotels")

        if not success:
            return False

        for hotel in hotels:
            if isinstance(hotel, dict) and hotel.get("id") == self.id:

                if nombre is not None:
                    hotel["nombre"] = nombre
                    self.nombre = nombre

                if estado is not None:
                    hotel["estado"] = estado
                    self.estado = estado

                if habitaciones is not None:
                    ocupadas = (
                        hotel.get("habitaciones", 0)
                        - hotel.get("habitaciones_disponibles", 0)
                    )
                    disponibles = habitaciones - ocupadas
                    hotel["habitaciones"] = habitaciones
                    hotel["habitaciones_disponibles"] = disponibles
                    self.habitaciones = habitaciones
                    self.habitaciones_disponibles = disponibles

                break
        else:
            logger.error("No se encontró hotel con ID %s", self.id)
            return False

        try:
            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(hotels, file, indent=2, ensure_ascii=False)

            logger.info("Hotel con ID %s modificado.", self.id)
            return True

        except (IOError, OSError) as error:
            logger.error("Error al escribir archivo: %s", error)
            return False

    def reserve_room(self, customer_id: int) -> bool:
        """Reserva una habitación en el hotel."""
        output_file = self.output_dir / "Hotels.json"
        success, hotels = load_json_file(output_file, "Hotels")

        if not success:
            return False

        for hotel in hotels:
            if isinstance(hotel, dict) and hotel.get("id") == self.id:

                disponibles = hotel.get("habitaciones_disponibles", 0)

                if disponibles <= 0:
                    logger.error(
                        "No hay habitaciones disponibles en hotel %s",
                        self.id,
                    )
                    return False

                hotel["habitaciones_disponibles"] = disponibles - 1
                self.habitaciones_disponibles = disponibles - 1
                break
        else:
            logger.error("No se encontró hotel con ID %s", self.id)
            return False

        try:
            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(hotels, file, indent=2, ensure_ascii=False)

            logger.info(
                "Habitación reservada en hotel %s para cliente %s",
                self.id,
                customer_id,
            )
            return True

        except (IOError, OSError) as error:
            logger.error("Error al escribir archivo: %s", error)
            return False

    def cancel_reservation(self, customer_id: int) -> bool:
        """Cancela una reservación y libera una habitación."""
        output_file = self.output_dir / "Hotels.json"
        success, hotels = load_json_file(output_file, "Hotels")

        if not success:
            return False

        for hotel in hotels:
            if isinstance(hotel, dict) and hotel.get("id") == self.id:

                disponibles = hotel.get("habitaciones_disponibles", 0)
                total = hotel.get("habitaciones", 0)

                if disponibles >= total:
                    logger.error(
                        "No hay reservaciones que cancelar en hotel %s",
                        self.id,
                    )
                    return False

                hotel["habitaciones_disponibles"] = disponibles + 1
                self.habitaciones_disponibles = disponibles + 1
                break
        else:
            logger.error("No se encontró hotel con ID %s", self.id)
            return False

        try:
            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(hotels, file, indent=2, ensure_ascii=False)

            logger.info(
                "Reservación cancelada en hotel %s para cliente %s",
                self.id,
                customer_id,
            )
            return True

        except (IOError, OSError) as error:
            logger.error("Error al escribir archivo: %s", error)
            return False


class Customer:
    """Clase para gestionar clientes."""

    output_dir = Path("Results")

    def __init__(
        self,
        nombre: str,
        email: str,
        telefono: str,
        customer_id: Optional[int] = None,
    ):
        self.id = customer_id
        self.nombre = nombre
        self.email = email
        self.telefono = telefono

    def create(self) -> bool:
        """Crea un nuevo cliente y lo guarda en Customers.json."""
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            output_file = self.output_dir / "Customers.json"

            customers = []
            if output_file.exists():
                success, customers = load_json_file(
                    output_file,
                    "Customers",
                )
                if not success:
                    customers = []

            new_id = 1
            if customers:
                try:
                    max_id = max(
                        c.get("id", 0)
                        for c in customers
                        if isinstance(c, dict)
                    )
                    new_id = max_id + 1
                except (ValueError, TypeError) as error:
                    logger.warning(
                        "Error calculando ID siguiente: %s. Usando ID 1.",
                        error,
                    )

            self.id = new_id

            customer_data = {
                "id": self.id,
                "nombre": self.nombre,
                "email": self.email,
                "telefono": self.telefono,
            }

            customers.append(customer_data)

            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(customers, file, indent=2, ensure_ascii=False)

            logger.info(
                "Cliente creado: ID %s - %s",
                self.id,
                self.nombre,
            )
            return True

        except (IOError, OSError) as error:
            logger.error("Error al escribir archivo: %s", error)
            return False

    def delete(self) -> bool:
        """Elimina un cliente."""
        output_file = self.output_dir / "Customers.json"
        success, customers = load_json_file(
            output_file,
            "Customers",
        )

        if not success:
            return False

        initial_count = len(customers)

        customers = [
            c for c in customers
            if isinstance(c, dict) and c.get("id") != self.id
        ]

        if len(customers) == initial_count:
            logger.error(
                "No se encontró cliente con ID %s",
                self.id,
            )
            return False

        try:
            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(customers, file, indent=2, ensure_ascii=False)

            logger.info("Cliente con ID %s eliminado.", self.id)
            return True

        except (IOError, OSError) as error:
            logger.error("Error al escribir archivo: %s", error)
            return False

    def display_info(self) -> dict[str, Any]:
        """Devuelve la información del cliente."""
        output_file = self.output_dir / "Customers.json"
        success, customers = load_json_file(
            output_file,
            "Customers",
        )

        if not success:
            return {}

        for customer in customers:
            if isinstance(customer, dict) and customer.get("id") == self.id:
                logger.info("Cliente encontrado: %s", customer)
                return customer

        logger.error("No se encontró cliente con ID %s", self.id)
        return {}

    def modify_info(
        self,
        nombre: Optional[str] = None,
        email: Optional[str] = None,
        telefono: Optional[str] = None,
    ) -> bool:
        """Modifica la información del cliente."""
        output_file = self.output_dir / "Customers.json"
        success, customers = load_json_file(
            output_file,
            "Customers",
        )

        if not success:
            return False

        for customer in customers:
            if isinstance(customer, dict) and customer.get("id") == self.id:

                if nombre is not None:
                    customer["nombre"] = nombre
                    self.nombre = nombre

                if email is not None:
                    customer["email"] = email
                    self.email = email

                if telefono is not None:
                    customer["telefono"] = telefono
                    self.telefono = telefono

                break
        else:
            logger.error(
                "No se encontró cliente con ID %s",
                self.id,
            )
            return False

        try:
            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(customers, file, indent=2, ensure_ascii=False)

            logger.info("Cliente con ID %s modificado.", self.id)
            return True

        except (IOError, OSError) as error:
            logger.error("Error al escribir archivo: %s", error)
            return False


class Reservation:
    """Clase para gestionar reservaciones."""

    output_dir = Path("Results")

    def __init__(
        self,
        customer_id: int,
        hotel_id: int,
        reservation_id: Optional[int] = None,
    ):
        self.id = reservation_id
        self.customer_id = customer_id
        self.hotel_id = hotel_id

    def _validate_customer(self) -> bool:
        """Verifica que el cliente exista."""
        customer = Customer("", "", "", self.customer_id)
        if not customer.display_info():
            logger.error(
                "Cliente con ID %s no existe.",
                self.customer_id,
            )
            return False
        return True

    def _validate_hotel(self) -> Hotel | None:
        """Verifica que el hotel exista."""
        hotel = Hotel("", "", 0, self.hotel_id)
        if not hotel.display_info():
            logger.error(
                "Hotel con ID %s no existe.",
                self.hotel_id,
            )
            return None
        return hotel

    def _generate_new_id(self, reservations: list) -> int:
        """Genera el siguiente ID disponible."""
        if not reservations:
            return 1

        try:
            max_id = max(
                r.get("id", 0)
                for r in reservations
                if isinstance(r, dict)
            )
            return max_id + 1
        except (ValueError, TypeError) as error:
            logger.warning(
                "Error calculando ID siguiente: %s. Usando ID 1.",
                error,
            )
            return 1

    def _load_reservations(self) -> list:
        """Carga las reservaciones desde archivo."""
        output_file = self.output_dir / "Reservations.json"

        if not output_file.exists():
            return []

        success, reservations = load_json_file(
            output_file,
            "Reservations",
        )
        return reservations if success else []

    def _save_reservations(self, reservations: list) -> bool:
        """Guarda las reservaciones en archivo."""
        output_file = self.output_dir / "Reservations.json"

        try:
            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(
                    reservations,
                    file,
                    indent=2,
                    ensure_ascii=False,
                )
            return True
        except (IOError, OSError) as error:
            logger.error(
                "Error al escribir archivo: %s",
                error,
            )
            return False

    def create(self) -> bool:
        """Crea una nueva reservación."""
        if not self._validate_customer():
            return False

        hotel = self._validate_hotel()
        if not hotel:
            return False

        if not hotel.reserve_room(self.customer_id):
            return False

        self.output_dir.mkdir(parents=True, exist_ok=True)

        reservations = self._load_reservations()

        self.id = self._generate_new_id(reservations)

        reservations.append(
            {
                "id": self.id,
                "customer_id": self.customer_id,
                "hotel_id": self.hotel_id,
            }
        )

        if not self._save_reservations(reservations):
            return False

        logger.info(
            "Reservación creada: ID %s - Cliente %s - Hotel %s",
            self.id,
            self.customer_id,
            self.hotel_id,
        )
        return True

    def cancel(self) -> bool:
        """Cancela una reservación."""
        reservations = self._load_reservations()

        reservation_found = next(
            (
                r for r in reservations
                if isinstance(r, dict) and r.get("id") == self.id
            ),
            None,
        )

        if not reservation_found:
            logger.error(
                "No se encontró reservación con ID %s",
                self.id,
            )
            return False

        hotel = Hotel(
            nombre="",
            estado="",
            habitaciones=0,
            hotel_id=reservation_found["hotel_id"],
        )

        if not hotel.cancel_reservation(
            reservation_found["customer_id"]
        ):
            return False

        reservations = [
            r for r in reservations
            if r.get("id") != self.id
        ]

        if not self._save_reservations(reservations):
            return False

        logger.info(
            "Reservación con ID %s cancelada correctamente.",
            self.id,
        )
        return True


if __name__ == "__main__":  # pragma: no cover
    logger.info("Sistema de reservación de hoteles")

    # Crear hoteles
    logger.info("Crear Hotel")
    hotel1 = Hotel("Grand Palace", "Veracruz", 100)
    hotel1.create()

    logger.info("Crear Hotel")
    hotel2 = Hotel("Fiesta Americana", "Puebla", 200)
    hotel2.create()

    # Mostrar información del hotel
    logger.info("Mostrar información del hotel")
    hotel1.display_info()

    # Modificar información del hotel
    logger.info("Modificar nombre y número de habitaciones del hotel")
    hotel1.modify_info(nombre="Grand Palace Hotel", habitaciones=200)

    logger.info("Verificar cambios")
    hotel1.display_info()

    # Crear clientes
    logger.info("Crear Cliente")
    customer1 = Customer("Anuar", "anuar@email.com", "2227709000")
    customer1.create()

    logger.info("Crear Cliente")
    customer2 = Customer("Alejandro", "Alejandro@email.com", "2227701234")
    customer2.create()

    # Mostrar información del cliente
    logger.info("Mostrar información del cliente")
    customer1.display_info()

    # Modificar información del cliente
    logger.info("Modificar Cliente")
    customer1.modify_info(
        nombre="Anuar Olmos Lopez",
        email="anuar.olmos@email.com",
    )

    logger.info("Verificar cambios")
    customer1.display_info()

    # Crear reservación
    logger.info("Crear Reservación")
    reservation1 = Reservation(customer1.id, hotel1.id)
    reservation1.create()

    logger.info("Crear Reservación 2")
    reservation2 = Reservation(customer2.id, hotel2.id)
    reservation2.create()

    # Verificar habitaciones disponibles
    logger.info("Verificar habitaciones disponibles del hotel")
    hotel1.display_info()

    # Cancelar reservación
    logger.info("Cancelar reservación 2")
    reservation2.cancel()

    # Verificar liberación de habitación
    logger.info("Verificar habitaciones disponibles del hotel")
    hotel1.display_info()

    # Eliminar cliente
    logger.info("Eliminar cliente")
    customer1.delete()

    # Eliminar hotel
    logger.info("Eliminar hotel")
    hotel1.delete()
