from worldathletics import WorldAthletics

# Initialize the client
wa = WorldAthletics()

print("WorldAthletics public methods/properties:")
for name in dir(wa):
    if not name.startswith("_"):
        print(" -", name)
