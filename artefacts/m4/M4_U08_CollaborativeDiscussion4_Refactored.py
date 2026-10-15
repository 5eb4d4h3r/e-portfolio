from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    """Defines the contract for computing a discounted price."""
    @abstractmethod
    def apply(self, price):
        pass

class BookDiscount(DiscountStrategy):
    RATE = 0.9
    def apply(self, price):
        return price * self.RATE

class ElectronicsDiscount(DiscountStrategy):
    RATE = 0.8
    def apply(self, price):
        return price * self.RATE

class NoDiscount(DiscountStrategy):
    def apply(self, price):
        return price

DISCOUNT_STRATEGIES = {
    'book': BookDiscount(),
    'electronics': ElectronicsDiscount(),
}

def calculate_total_price(items):
    """Sum item prices, delegating the discount rule to a strategy object.
    A new item type is added by writing a new DiscountStrategy subclass
    and registering it in DISCOUNT_STRATEGIES; this function does not change.
    """
    total = 0
    for item in items:
        strategy = DISCOUNT_STRATEGIES.get(item['type'], NoDiscount())
        total += strategy.apply(item['price'])
    return total

# Sample test line:
sample_items = [
    {'type': 'book', 'price': 100},
    {'type': 'electronics', 'price': 200},
    {'type': 'other', 'price': 50}
]

print(f"{'Item Type':<15} | {'Original':<10} | {'Discounted':<10}")
print("-" * 42)

for item in sample_items:
    # Pass each item individually to calculate its discounted price
    discounted_price = calculate_total_price([item])
    print(f"{item['type']:<15} | ${item['price']:<9.2f} | ${discounted_price:<9.2f}")

print("-" * 42)

# Pass all items together to calculate the grand total
final_total = calculate_total_price(sample_items)
print(f"Total Price: ${final_total:.2f}")