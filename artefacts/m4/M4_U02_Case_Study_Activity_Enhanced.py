"""
M4 Unit 2 Case Study Activity: Enhanced code.

Refactors the original Order class to comply with the SOLID principles
covered in Unit 2. Each class below has a single, clearly stated
responsibility, and payment handling depends on an abstraction rather
than on concrete payment classes.
"""

from abc import ABC, abstractmethod


class Product:
    """Represents a single item available for purchase."""
    def __init__(self, name: str, price: float) -> None:
        self.name = name
        self.price = price


class Order:
    """
    Manages the items in a shopping cart and calculates the total price.

    Handles cart-related responsibility only, per the Single
    Responsibility Principle. Payment handling has been moved out to
    PaymentProcessor and the PaymentMethod hierarchy below.
    """
    def __init__(self) -> None:
        self.items = []

    def add_item(self, item: Product) -> None:
        self.items.append(item)

    def calculate_total(self) -> float:
        return sum(item.price for item in self.items)


class PaymentMethod(ABC):
    """
    Abstraction that every concrete payment strategy must implement.

    Kept to a single method so that no implementing class is ever forced
    to support an operation it does not need, per the Interface
    Segregation Principle.
    """
    @abstractmethod
    def pay(self, amount: float) -> None:
        ...


class CreditCardPayment(PaymentMethod):
    def pay(self, amount: float) -> None:
        print(f"Processing credit card payment of {amount:.2f}.")


class PayPalPayment(PaymentMethod):
    def pay(self, amount: float) -> None:
        print(f"Processing PayPal payment of {amount:.2f}.")


class CryptoPayment(PaymentMethod):
    """
    Added after the fact, without any change to PaymentProcessor or to
    the two payment classes above, demonstrating the Open/Closed
    Principle in practice.
    """
    def pay(self, amount: float) -> None:
        print(f"Processing cryptocurrency payment of {amount:.2f}.")


class PaymentProcessor:
    """
    Delegates execution to whichever PaymentMethod it is given.

    Depends on the PaymentMethod abstraction rather than a concrete
    class, per the Dependency Inversion Principle. Any current or
    future PaymentMethod subclass can be substituted here without
    altering this class, per the Liskov Substitution Principle.
    """
    def __init__(self, payment_method: PaymentMethod) -> None:
        self.payment_method = payment_method

    def process(self, amount: float) -> None:
        self.payment_method.pay(amount)


if __name__ == "__main__":
    # Same test inputs and same four test labels as
    # M4_U02_Case_Study_Activity_Original.py, so the two files can be
    # compared step for step (45.00 + 210.00 = 255.00).
    order = Order()
    order.add_item(Product("Keyboard", 45.00))
    order.add_item(Product("Monitor", 210.00))

    print("Test 1: Sum of items in the cart.")
    total = order.calculate_total()
    print(f"Cart total: {total}")
    assert total == 255.00, "Total does not match the sum of item prices."
    print("Result: total matches the expected value.\n")

    print("Test 2: Credit card payment method.")
    PaymentProcessor(CreditCardPayment()).process(total)
    print()

    print("Test 3: PayPal payment method.")
    PaymentProcessor(PayPalPayment()).process(total)
    print()

    print("Test 4: New payment method (cryptocurrency), added without "
          "modifying PaymentProcessor or any existing payment class.")
    PaymentProcessor(CryptoPayment()).process(total)
    # Unlike the original file, this produces real output. Compare this
    # result directly against Test 4 in the original file: there, the
    # equivalent call produced nothing, because supporting a new payment
    # type required editing pay() itself.
    print("Result: cryptocurrency payment processed correctly, with no "
          "change required to PaymentProcessor or to any existing "
          "payment class. Compare against Test 4 in the original file.")