from abc import ABC, abstractmethod

# Car Interface/Abstract Class
class Car(ABC):
    """Abstract product: any car must implement drive()."""
    @abstractmethod
    def drive(self):
        pass

# Concrete Car Classes
class Sedan(Car):
    def drive(self):
        print("Sedan is driving smoothly on the highway.")

class SUV(Car):
    def drive(self):
        print("SUV is driving confidently off-road.")

class Hatchback(Car):
    def drive(self):
        print("Hatchback is driving nimbly through city traffic.")

# CarFactory Abstract Class
class CarFactory(ABC):
    """Abstract creator. Defers car instantiation to its subclasses.
    To add a new car type, create a Car subclass and a matching
    CarFactory subclass overriding create_car(). Car, CarFactory and
    every existing car/factory class stay unchanged; only main() needs
    a one-line addition, adding the new factory to its list, to
    demonstrate the new type."""

    @abstractmethod
    def create_car(self):
        pass

# Concrete Factories
class SedanFactory(CarFactory):
    def create_car(self):
        return Sedan()

class SUVFactory(CarFactory):
    def create_car(self):
        return SUV()

class HatchbackFactory(CarFactory):
    def create_car(self):
        return Hatchback()

# Factory Method Pattern / Main program
def main():
    """Client code: depends only on the CarFactory and Car abstractions,
    not on any concrete car class."""
    factories = [SedanFactory(), SUVFactory(), HatchbackFactory()]
    for factory in factories:
        car = factory.create_car()
        car.drive()

main()