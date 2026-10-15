class Vehicle:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

    def display_details(self):
        details = {
            "Type": self.__class__.__name__,
            "Brand": self.brand,
            "Model": self.model,
        }
        details.update(self._identifier_field())
        return details

    def _identifier_field(self):
        raise NotImplementedError("Subclasses must implement _identifier_field()")


class Car(Vehicle):
    def __init__(self, brand, model, chassis_id):
        super().__init__(brand, model)
        self.__chassis_id = chassis_id  # private, specific to Car

    def _identifier_field(self):
        return {"ID": "Access restricted"}


class Bike(Vehicle):
    def __init__(self, brand, model, serial_number):
        super().__init__(brand, model)
        self.__serial_number = serial_number  # private, specific to Bike

    def _identifier_field(self):
        return {"ID": "Access restricted"}


def print_table(rows: list[dict]):
    if not rows:
        print("No vehicles to display.")
        return

    headers = list(rows[0].keys())
    col_widths = {h: max(len(h), max(len(str(r[h])) for r in rows)) for h in headers}

    header_line = " | ".join(h.ljust(col_widths[h]) for h in headers)
    print(header_line)
    print("-+-".join("-" * col_widths[h] for h in headers))

    for row in rows:
        print(" | ".join(str(row[h]).ljust(col_widths[h]) for h in headers))


cars = [
    Car("Dodge", "Dodge", "UScar-88213"),
    Car("Tesla", "Model Y", "US-77410"),
    Car("Rolls-Royce", "Phantom", "UK-90921"),
]

bikes = [
    Bike("Honda", "CB500", "SN-40217"),
    Bike("Yamaha", "MT-07", "SN-51830"),
]

vehicles = {"car": cars, "bike": bikes}

choice = input("Select a vehicle type to list (car/bike): ").strip().lower()

if choice in vehicles:
    print_table([v.display_details() for v in vehicles[choice]])
else:
    print("Unknown selection.")