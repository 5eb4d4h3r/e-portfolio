from abc import ABC, abstractmethod


#Component interface: any coffee must expose a description.
class Coffee(ABC):
    @abstractmethod
    def description(self):
        pass

#Concrete component: the base object being decorated.
class SimpleCoffee(Coffee):
    def description(self):
        return "Coffee"

#    """Concrete component: the base object being decorated."""
class CoffeeDecorator(Coffee):
    """Decorator base: wraps a Coffee and forwards calls to it."""

    def __init__(self, wrapped_coffee):
        self._wrapped_coffee = wrapped_coffee

    def description(self):
        return self._wrapped_coffee.description()


class MilkDecorator(CoffeeDecorator):
    def description(self):
        return self._wrapped_coffee.description() + " with milk"


class SugarDecorator(CoffeeDecorator):
    def description(self):
        return self._wrapped_coffee.description() + " with sugar"


if __name__ == "__main__":
    order = SimpleCoffee()
    order = MilkDecorator(order)
    order = SugarDecorator(order)

    print(order.description())