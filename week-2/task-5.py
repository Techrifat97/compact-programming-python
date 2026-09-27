events = {
    "Mit VR die Museen der Welt entdecken": "19.09.2026",
    "Unter der Lupe": "19.09.2026",
    "Der Schmied und das heisse Eisen": "19.09.2026",
    "Connected - Digitale Kultur im Ruhrgebiet": "19.09.2026",
    "Schloss der Arbeit": "19.09.2026",
    "Nachts im Museum": "19.09.2026",
    "Die DEW21 Museumsnacht tanzt": "19.09.2026"
}

museum_night = "19.09.2026"

print("Events during the Night of Museums in Dortmund:")

for event, date in events.items():
    if date == museum_night:
        print(event)