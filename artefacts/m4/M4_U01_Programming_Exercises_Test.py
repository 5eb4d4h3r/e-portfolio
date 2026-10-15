"""
Unit tests for the Unit 1 OOP exercises.

Run with: python3 -m unittest M4_U01_Programming_Exercises_Test.py -v
"""

import io
import unittest
from contextlib import redirect_stdout
from M4_U01_Programming_Exercises import (
    Vehicle,
    Car,
    Shape,
    Circle,
    Rectangle,
    BankAccount,
    Animal,
    Dog,
    Cat,
    Person,
)


class TestVehicleAndCar(unittest.TestCase):
    def test_vehicle_attributes(self):
        v = Vehicle("Honda", "Diesel")
        self.assertEqual(v.brand, "Honda")
        self.assertEqual(v.fuel_type, "Diesel")

    def test_car_inherits_parent_init(self):
        c = Car("Toyota", "Petrol", 4)
        self.assertEqual(c.brand, "Toyota")
        self.assertEqual(c.fuel_type, "Petrol")
        self.assertEqual(c.num_doors, 4)

    def test_car_is_a_vehicle(self):
        c = Car("Ford", "Hybrid", 2)
        self.assertIsInstance(c, Vehicle)


class TestShapePolymorphism(unittest.TestCase):
    def test_circle_area(self):
        self.assertAlmostEqual(Circle(2.0).area(), 12.566370614359172)

    def test_rectangle_area(self):
        self.assertEqual(Rectangle(4.0, 5.0).area(), 20.0)

    def test_cannot_instantiate_abstract_shape(self):
        with self.assertRaises(TypeError):
            Shape()


class TestBankAccount(unittest.TestCase):
    def test_deposit_increases_balance(self):
        acc = BankAccount(100.0)
        acc.deposit(50.0)
        self.assertEqual(acc.get_balance(), 150.0)

    def test_withdraw_decreases_balance(self):
        acc = BankAccount(100.0)
        acc.withdraw(30.0)
        self.assertEqual(acc.get_balance(), 70.0)

    def test_withdraw_insufficient_funds_raises(self):
        acc = BankAccount(50.0)
        with self.assertRaises(ValueError):
            acc.withdraw(100.0)

    def test_balance_attribute_is_not_directly_accessible(self):
        acc = BankAccount(10.0)
        with self.assertRaises(AttributeError):
            _ = acc.__balance  # name-mangled, not accessible as written


class TestAnimalSounds(unittest.TestCase):
    def test_dog_sound(self):
        self.assertEqual(Dog().make_sound(), "Woof!")

    def test_cat_sound(self):
        self.assertEqual(Cat().make_sound(), "Meow!")

    def test_cannot_instantiate_abstract_animal(self):
        with self.assertRaises(TypeError):
            Animal()


class TestPersonConstructorDestructor(unittest.TestCase):
    def test_name_assigned_on_construction(self):
        p = Person("Grace")
        self.assertEqual(p.name, "Grace")

    def test_del_prints_farewell_message(self):
        output = io.StringIO()
        with redirect_stdout(output):
            p = Person("Ada")
            del p
        self.assertEqual(output.getvalue(), "Goodbye, Ada!\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)