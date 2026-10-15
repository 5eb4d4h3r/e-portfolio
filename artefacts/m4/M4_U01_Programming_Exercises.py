"""
Advanced Object-Oriented Design and Programming
Unit 1 lab exercises: Classes, Objects, Access Control, Inheritance,
Polymorphism, Abstraction, and Encapsulation.
"""

from abc import ABC, abstractmethod
import math


# ---------------------------------------------------------------------------
# Task 1: Basic class hierarchy (inheritance)
# ---------------------------------------------------------------------------
class Vehicle:
    """Base class representing a generic vehicle."""

    def __init__(self, brand: str, fuel_type: str) -> None:
        self.brand = brand
        self.fuel_type = fuel_type

    def describe(self) -> str:
        return f"{self.brand} ({self.fuel_type})"


class Car(Vehicle):
    """Specialises Vehicle for the is-a relationship car-is-a-vehicle."""

    def __init__(self, brand: str, fuel_type: str, num_doors: int) -> None:
        super().__init__(brand, fuel_type)
        self.num_doors = num_doors

    def describe(self) -> str:
        return f"{super().describe()}, {self.num_doors}-door"


# ---------------------------------------------------------------------------
# Task 2: Polymorphism with methods
# ---------------------------------------------------------------------------
class Shape(ABC):
    """Abstract superclass defining the shape protocol."""

    @abstractmethod
    def area(self) -> float:
        """Return the area of the shape. No default implementation exists."""
        raise NotImplementedError


class Circle(Shape):
    def __init__(self, radius: float) -> None:
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2


class Rectangle(Shape):
    def __init__(self, length: float, width: float) -> None:
        self.length = length
        self.width = width

    def area(self) -> float:
        return self.length * self.width


# ---------------------------------------------------------------------------
# Task 3: Encapsulation with access control
# ---------------------------------------------------------------------------
class BankAccount:
    """Wraps a balance so that state changes are validated centrally."""

    def __init__(self, initial_balance: float = 0.0) -> None:
        self.__balance = initial_balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.__balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self.__balance:
            raise ValueError("Insufficient funds.")
        self.__balance -= amount

    def get_balance(self) -> float:
        return self.__balance


# ---------------------------------------------------------------------------
# Task 4: Abstraction with a base class
# ---------------------------------------------------------------------------
class Animal(ABC):
    """Abstract superclass; every Animal must define how it sounds."""

    @abstractmethod
    def make_sound(self) -> str:
        raise NotImplementedError


class Dog(Animal):
    def make_sound(self) -> str:
        return "Woof!"


class Cat(Animal):
    def make_sound(self) -> str:
        return "Meow!"


# ---------------------------------------------------------------------------
# Task 5: Constructor and destructor
# ---------------------------------------------------------------------------
class Person:
    def __init__(self, name: str) -> None:
        self.name = name

    def __del__(self) -> None:
        print(f"Goodbye, {self.name}!")


# ---------------------------------------------------------------------------
# Demonstration / manual test harness
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    car = Car("Toyota", "Petrol", 4)
    print(car.describe())

    shapes: list[Shape] = [Circle(3.0), Rectangle(4.0, 5.0)]
    for shape in shapes:
        print(f"{type(shape).__name__} area: {shape.area():.2f}")

    account = BankAccount(100.0)
    account.deposit(50.0)
    account.withdraw(30.0)
    print(f"Balance: {account.get_balance():.2f}")
    try:
        account.withdraw(1000.0)
    except ValueError as exc:
        print(f"Withdrawal rejected: {exc}")

    animals: list[Animal] = [Dog(), Cat()]
    for animal in animals:
        print(f"{type(animal).__name__} says {animal.make_sound()}")

    p = Person("Ada")
    del p