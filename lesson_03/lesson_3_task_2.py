from smartphone import Smartphone

Catalog = [
    Smartphone("Apple", "iPhone 13", "+79999999999"),
    Smartphone("Samsung", "Galaxy S21", "+79999999998"),
    Smartphone("Xiaomi", "17Pro", "+79999999997"),
    Smartphone("Google", "Pixel", "+79999999996"),
    Smartphone("Oppo", "Find1", "+79999999995")
]
for phone in Catalog:
    print(f"{phone.brand} - {phone.model}. {phone.phone_number}")
