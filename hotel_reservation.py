import json
from pathlib import Path
from typing import Optional, Dict


class Hotel:
    """Clase para gestionar hoteles.

    Attributes:
        output_dir: Directorio donde se guardan los archivos JSON.
        id: Identificador único del hotel.
        nombre: Nombre del hotel.
        estado: Estado/ubicación del hotel.
        habitaciones: Número total de habitaciones.
        habitaciones_disponibles: Habitaciones disponibles para reservar.

    Gestiona la información y operaciones de hoteles, incluyendo crear,
    eliminar, modificar y mostrar información. También se encarga de la
    persistencia de datos en archivos JSON.
    """
    output_dir = Path("Results")

    @staticmethod
    def _load_json_file(file_path: Path, file_type: str):
        """Carga y valida un archivo JSON.

        Args:
            file_path: Ruta al archivo JSON.
            file_type: Tipo de archivo para mensajes de error.

        Returns:
            tuple: (success: bool, data: list)
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

        Returns:
            bool: True si se creó exitosamente, False en caso contrario.
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

        Returns:
            bool: True si se eliminó exitosamente, False en caso contrario.
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

        Returns:
            Dict: Diccionario con la información del hotel o {} si no existe.
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
    hotel2.display_info()

    print("\n Eliminar hotel")
    hotel1.delete()
    hotel2.delete()
