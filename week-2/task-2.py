# Week 2 - Task 2

s1 = "Python 3 is easy 123"

total = 0
count = 0

for character in s1:
    if character.isdigit():
        total += int(character)
        count += 1

if count > 0:
    average = total / count

    print("Sum:", total)
    print("Average:", average)
else:
    print("No digits found")