import json
from pathlib import Path
from typing import Optional, Dict


class Hotel:
    """Clase para gestionar hoteles.


    """
    output_dir = Path("Results")

    @staticmethod
    def _load_json_file(file_path: Path, file_type: str):
        """Carga y valida un archivo JSON.

        """
        if not file_path.exists():
            print(f"Error: El archivo {file_type}.json no existe.")
            return False, []

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                if not content:
                    print("Error: El archivo está vacío.")
                    return False, []
                data = json.loads(content)
                if not isinstance(data, list):
                    print(f"Error: Invalid data format in {file_type}.json.")
                    return False, []
                return True, data
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {file_type}.json: {e}")
            return False, []

    def __init__(self, nombre: str, estado: str, habitaciones: int,
                 hotel_id: Optional[int] = None):
        self.id = hotel_id
        self.nombre = nombre
        self.estado = estado
        self.habitaciones = habitaciones
        self.habitaciones_disponibles = habitaciones

    def create(self) -> bool:
        """Crea un nuevo hotel y lo guarda en Hotels.json.


        """
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            output_file = self.output_dir / "Hotels.json"

            hotels = []
            if output_file.exists():
                try:
                    with open(output_file, 'r', encoding='utf-8') as file:
                        content = file.read().strip()
                        if content:
                            hotels = json.loads(content)
                            if not isinstance(hotels, list):
                                print(
                                    "Error: Invalid data format in "
                                    "Hotels.json. Expected a list. "
                                    "Continuing with empty list.")
                                hotels = []
                except json.JSONDecodeError as e:
                    print(f"Error: Invalid JSON in Hotels.json: {e}. "
                          "Continuing with empty list.")
                    hotels = []

            new_id = 1
            if hotels:
                try:
                    max_id = max(
                        h.get('id', 0) for h in hotels
                        if isinstance(h, dict)
                    )
                    new_id = max_id + 1
                except (ValueError, TypeError) as e:
                    print(f"Error calculating next ID: {e}. Using ID 1.")

            self.id = new_id

            hotel_data = {
                'id': self.id,
                'nombre': self.nombre,
                'estado': self.estado,
                'habitaciones': self.habitaciones,
                'habitaciones_disponibles': self.habitaciones_disponibles
            }
            hotels.append(hotel_data)

            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(hotels, file, indent=2, ensure_ascii=False)

            print(f"Hotel creado: ID {self.id}, {self.nombre} "
                  f"en {self.estado}")
            return True

        except (IOError, OSError) as error:
            print(f"Error al escribir en archivo: {error}")
            return False

    def delete(self) -> bool:
        """Elimina el hotel del archivo Hotels.json.

        """
        output_file = self.output_dir / "Hotels.json"
        success, hotels = self._load_json_file(output_file, "Hotels")

        if not success:
            return False

        initial_count = len(hotels)
        hotels = [
            h for h in hotels
            if isinstance(h, dict) and h.get('id') != self.id
        ]

        if len(hotels) == initial_count:
            print(f"Error: No se encontró hotel con ID {self.id}")
            return False

        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(hotels, file, indent=2, ensure_ascii=False)
            print(f"Hotel con ID {self.id} eliminado correctamente.")
            return True
        except (IOError, OSError) as error:
            print(f"Error al escribir en archivo: {error}")
            return False

    def display_info(self) -> Dict:
        """Muestra la información del hotel.

        """
        output_file = self.output_dir / "Hotels.json"
        success, hotels = self._load_json_file(output_file, "Hotels")

        if not success:
            return {}

        for hotel in hotels:
            if isinstance(hotel, dict) and hotel.get('id') == self.id:
                print(f"Hotel ID: {hotel.get('id')}")
                print(f"Nombre: {hotel.get('nombre')}")
                print(f"Estado: {hotel.get('estado')}")
                print(
                    f"Habitaciones totales: "
                    f"{hotel.get('habitaciones')}"
                )
                print(f"Habitaciones disponibles: "
                      f"{hotel.get('habitaciones_disponibles')}")
                return hotel

        print(f"Error: No se encontró hotel con ID {self.id}")
        return {}

    def _update_hotel_data(self, hotel: dict, nombre, estado, habitaciones):
        """Actualiza los datos de un hotel."""
        if nombre is not None:
            hotel['nombre'] = nombre
            self.nombre = nombre
        if estado is not None:
            hotel['estado'] = estado
            self.estado = estado
        if habitaciones is not None:
            ocupadas = hotel.get('habitaciones', 0) - hotel.get(
                'habitaciones_disponibles', 0)
            new_disponibles = habitaciones - ocupadas
            hotel['habitaciones'] = habitaciones
            hotel['habitaciones_disponibles'] = new_disponibles
            self.habitaciones = habitaciones
            self.habitaciones_disponibles = new_disponibles

    def modify_info(self, nombre: Optional[str] = None,
                    estado: Optional[str] = None,
                    habitaciones: Optional[int] = None) -> bool:
        """Modifica la información del hotel.

        """
        output_file = self.output_dir / "Hotels.json"
        success, hotels = self._load_json_file(output_file, "Hotels")

        if not success:
            return False

        hotel_found = False
        for hotel in hotels:
            if isinstance(hotel, dict) and hotel.get('id') == self.id:
                self._update_hotel_data(hotel, nombre, estado, habitaciones)
                hotel_found = True
                break

        if not hotel_found:
            print(f"Error: No se encontró hotel con ID {self.id}")
            return False

        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(hotels, file, indent=2, ensure_ascii=False)
            print(f"Hotel con ID {self.id} modificado correctamente.")
            return True
        except (IOError, OSError) as error:
            print(f"Error al escribir en archivo: {error}")
            return False

    def reserve_room(self, customer_id: int) -> bool:
        """Reserva una habitación en el hotel.

    


        """
        output_file = self.output_dir / "Hotels.json"
        success, hotels = self._load_json_file(output_file, "Hotels")

        if not success:
            return False

        hotel_found = False
        for hotel in hotels:
            if isinstance(hotel, dict) and hotel.get('id') == self.id:
                disponibles = hotel.get('habitaciones_disponibles', 0)
                if disponibles <= 0:
                    print(f"Error: No hay habitaciones disponibles "
                          f"en el hotel {self.id}")
                    return False
                hotel['habitaciones_disponibles'] = disponibles - 1
                self.habitaciones_disponibles = disponibles - 1
                hotel_found = True
                break

        if not hotel_found:
            print(f"Error: No se encontró hotel con ID {self.id}")
            return False

        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(hotels, file, indent=2, ensure_ascii=False)
            print(f"Habitación reservada en hotel {self.id} "
                  f"para cliente {customer_id}")
            return True
        except (IOError, OSError) as error:
            print(f"Error al escribir en archivo: {error}")
            return False

    def cancel_reservation(self, customer_id: int) -> bool:
        """Cancela una reservación y libera una habitación.

        Args:
            customer_id: ID del cliente que cancela la reservación.


        """
        output_file = self.output_dir / "Hotels.json"
        success, hotels = self._load_json_file(output_file, "Hotels")

        if not success:
            return False

        hotel_found = False
        for hotel in hotels:
            if isinstance(hotel, dict) and hotel.get('id') == self.id:
                disponibles = hotel.get('habitaciones_disponibles', 0)
                total = hotel.get('habitaciones', 0)
                if disponibles >= total:
                    print(f"Error: No hay reservaciones que cancelar "
                          f"en el hotel {self.id}")
                    return False
                hotel['habitaciones_disponibles'] = disponibles + 1
                self.habitaciones_disponibles = disponibles + 1
                hotel_found = True
                break

        if not hotel_found:
            print(f"Error: No se encontró hotel con ID {self.id}")
            return False

        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(hotels, file, indent=2, ensure_ascii=False)
            print(f"Reservación cancelada en hotel {self.id} "
                  f"para cliente {customer_id}")
            return True
        except (IOError, OSError) as error:
            print(f"Error al escribir en archivo: {error}")
            return False

if __name__ == "__main__":
    print("\n Sistema de reservación de hoteles")

    # Crear hoteles
    print("\n Crear Hotel ")
    hotel1 = Hotel("Grand Palace", "Veracruz", 100)
    hotel1.create()
    print("\n Crear Hotel ")
    hotel2 = Hotel("Fiesta Americana", "Puebla", 200)
    hotel2.create()

    print("\n Mostrar información del hotel")
    hotel1.display_info()

    print("\n Modificar información del hotel")
    hotel1.modify_info("Fiesta Americana", "Puebla", 200)

    print("\n Mostrar información del hotel")
    hotel1.display_info()


    print("\n Eliminar hotel")
    hotel2.delete()

