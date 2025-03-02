
# list of random names
list_of_names = ["John", "Jane", "Jack", "Jill", "James", "Jenny", "Jasper", "Jade", "Jared", "Jasmine"]

for name in list_of_names:
    print(name)

print("\n")

for name in list_of_names[:4]:
    print(name)
print("\n")

for name in list_of_names[0:4]:
    print(name)
print("\n")

for name in list_of_names[:-2]:
    print(name)

print("\n")

for i, name in enumerate(list_of_names):
    print(f"{i}: {name}")
print("\n")

for i in range(len(list_of_names)):
    print(f"{i}: {list_of_names[i]}")

if len(list_of_names) < 3:
    print("List is too short")
else:
    print("List is long enough")


# a random dictionary of countries and their capitals
countries_and_capitals = {
    "Nigeria": "Abuja",
    "Ghana": "Accra",
    "Kenya": "Nairobi",
    "South Africa": "Cape Town",
    "Egypt": "Cairo",
    "Morocco": "Rabat",
    "Algeria": "Algiers",
}

for country in countries_and_capitals:
    print(f"{country}: {countries_and_capitals[country]}")

for country, capital in countries_and_capitals.items():
    print(f"{country}: {capital}")

for country in countries_and_capitals.keys():
    print(country)

for capital in countries_and_capitals.values():
    print(capital)

for country in countries_and_capitals:
    print(country)

for i, (country, capital) in enumerate(countries_and_capitals.items()):
    print(f"{i}: {country}: {capital}")