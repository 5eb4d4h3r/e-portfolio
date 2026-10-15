# Example 1: Excessive Literal Use ==> Introduce Constant
#--------------------------------------------------------

BOOK_DISCOUNT = 0.9                  # named constant replacing the bare literal 0.9, this is the target of Introduce Constant
ELECTRONICS_DISCOUNT = 0.8           # named constant replacing the bare literal 0.8, same rationale as above

def calculate_total_price_1(items):    # entry point that sums the total price across a collection of items
    total = 0                        # accumulator, starts at zero before the loop runs
    for item in items:               # iterate over each item dictionary in the input list
        if item['type'] == 'book':                         # branch for the book category
            total += item['price'] * BOOK_DISCOUNT         # apply the named constant instead of the magic number 0.9
        elif item['type'] == 'electronics':                # branch for the electronics category
            total += item['price'] * ELECTRONICS_DISCOUNT  # apply the named constant instead of the magic number 0.8
        else:                         # fallback branch for any other item type
            total += item['price']    # no discount applies, full price is added
    return total                      # return the accumulated total to the caller


# Example 2: Long Method ==> Replace Conditional with Polymorphism
#-----------------------------------------------------------------

from abc import ABC, abstractmethod          # import the tools needed to declare an abstract base class

class DiscountStrategy(ABC):                 # abstract base class defining the strategy interface
    """Defines the contract for computing a discounted price."""
    @abstractmethod                          # marks apply() as mandatory for every subclass
    def apply(self, price):                  # the one method every concrete strategy must implement
        pass                                 # no implementation here, this class only defines the shape of the contract

class BookDiscount(DiscountStrategy):        # concrete strategy for the book category
    RATE = 0.9                               # book-specific discount rate, scoped to this class rather than  globally
    def apply(self, price):                  # implements the contract for books
        return price * self.RATE             # applies the book rate to the given price

class ElectronicsDiscount(DiscountStrategy): # concrete strategy for the electronics category
    RATE = 0.8                               # electronics-specific discount rate
    def apply(self, price):                  # implements the contract for electronics
        return price * self.RATE             # applies the electronics rate to the given price

class NoDiscount(DiscountStrategy):          # Null Object representing "no applicable discount" without a branch
    def apply(self, price):                  # implements the contract for any other category
        return price                         # returns the price unchanged, this is the default case

DISCOUNT_STRATEGIES = {                      # registry mapping an item type string to its strategy instance
    'book': BookDiscount(),                  # one shared BookDiscount instance for all book items
    'electronics': ElectronicsDiscount(),    # one shared ElectronicsDiscount instance for all electronics items
}

def calculate_total_price_2(items):            # entry point, now free of any type-specific branching
    """
    A new item type is added by writing a new DiscountStrategy subclass
    and registering it in DISCOUNT_STRATEGIES; this function does not change.
    """
    total = 0                                # accumulator, starts at zero before the loop runs
    for item in items:                       # iterate over each item dictionary, same as before
        strategy = DISCOUNT_STRATEGIES.get(item['type'], NoDiscount())  # look up the matching strategy, fall back to NoDiscount
        total += strategy.apply(item['price'])   # delegate the actual calculation to the selected strategy object
    return total                             # return the accumulated total to the caller


# Manual demonstration: run the sample basket through both functions directly
# ---------------------------------------------------------------------------
sample_items = [
    {'type': 'book', 'price': 50},
    {'type': 'book', 'price': 20},
    {'type': 'electronics', 'price': 200},
    {'type': 'toy', 'price': 15},
]
if __name__ == '__main__':  # runs this block only when the file is executed directly
    total_1 = calculate_total_price_1(sample_items)
    total_2 = calculate_total_price_2(sample_items)
    print(f"Total (Example 1, Introduce Constant): {total_1}")
    print(f"Total (Example 2, Strategy Pattern): {total_2}")
