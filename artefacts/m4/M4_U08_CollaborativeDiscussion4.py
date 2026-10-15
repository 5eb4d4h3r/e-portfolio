def calculate_total_price(items):
    total = 0
    for item in items:
        if item['type'] == 'book':
            total += item['price'] * 0.9 # 10% discount for books
        elif item['type'] == 'electronics':
            total += item['price'] * 0.8 # 20% discount for electronics
        else:
            total += item['price']
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