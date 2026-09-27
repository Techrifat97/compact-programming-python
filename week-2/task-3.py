# Week 2 - Task 3

phones = [
    {'make': 'Google', 'model': 216, 'color': 'Black'},
    {'make': 'Mi Max', 'model': '2', 'color': 'Gold'},
    {'make': 'Samsung', 'model': 7, 'color': 'Blue'}
]

phones.sort(key=lambda phone: phone['color'])

print(phones)