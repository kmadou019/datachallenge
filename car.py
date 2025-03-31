#!/usr/bin/env python3

from codecarbon import EmissionsTracker
import time

tracker = EmissionsTracker()

# Première section du code
tracker.start()
time.sleep(2)  # Simulation d'un calcul
for i in range(1000000):
    pass  # Simuler un calcul lourd
emission_1 = tracker.stop()
print(emission_1)

# Deuxième section du code
tracker.start()
time.sleep(3)  # Simulation d'un autre calcul
emission_2 = tracker.stop()
print(f"Émissions section 2: {emission_2:.6f} kg CO₂")
