numbers = [(2, 5), (1, 2), (4, 4), (2, 3), (2, 1)]

def last_element(item):
    return item[-1]

numbers.sort(key=last_element)

print("Sorted list:", numbers)