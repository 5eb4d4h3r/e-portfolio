"""
M4 Unit 2 Case Study Activity: Original code.

The Order class below is reproduced exactly as issued in the activity
brief. It is left unmodified so that its Single Responsibility Principle,
Open/Closed Principle, and Dependency Inversion Principle violations can
be observed directly, before any refactoring is attempted in the
companion file M4_U02_Case_Study_Activity_Enhanced.py.
"""


class Order:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def calculate_total(self):
        return sum(item.price for item in self.items)

    def pay(self, payment_type):
        if payment_type == "credit":
            print("Processing credit card payment...")
        elif payment_type == "paypal":
            print("Processing PayPal payment...")
        # Adding a new method requires modifying this class.


class Item:
    """
    Not part of the original snippet. Added only because Order.add_item()
    expects an object with a .price attribute, and no such class was
    provided in the brief. Nothing above this class has been changed.
    """
    def __init__(self, name, price):
        self.name = name
        self.price = price


if __name__ == "__main__":
    # Test inputs: prices chosen so the expected total is easy to verify
    # by hand (45.00 + 210.00 = 255.00). The same inputs and the same
    # four test labels are reused in M4_U02_Case_Study_Activity_Enhanced.py
    # so the two files can be compared step for step.
    order = Order()
    order.add_item(Item("Keyboard", 45.00))
    order.add_item(Item("Monitor", 210.00))

    print("Test 1: Sum of items in the cart.")
    total = order.calculate_total()
    print(f"Cart total: {total}")
    assert total == 255.00, "Total does not match the sum of item prices."
    print("Result: total matches the expected value.\n")

    print("Test 2: Credit card payment method.")
    order.pay("credit")
    print()

    print("Test 3: PayPal payment method.")
    order.pay("paypal")
    print()

    print("Test 4: New payment method (cryptocurrency), not supported by "
          "the original code.")
    order.pay("crypto")
    # No branch in pay() matches "crypto", so the call above produces no
    # output and raises no error. That silence is the result being
    # tested for: it is the evidence of the Open/Closed Principle
    # violation, since a new payment type cannot be supported without
    # editing the body of pay() directly.
    # print("Result: no output line appears above this one. pay() has no "
    #      "branch for 'crypto', so the call above did nothing. Adding "
    #      "support requires editing pay() directly, which is the "
    #      "Open/Closed Principle violation.")