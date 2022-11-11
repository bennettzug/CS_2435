desiredWeight = int(input("Enter desired weight: "))
tolerance = int(input("Enter tolerance (as percentage): ")) * .01
minWeight = desiredWeight - tolerance * desiredWeight
maxWeight = desiredWeight + tolerance * desiredWeight
print(f"The range of accepted weight for the part is from {minWeight:.1f} to {maxWeight:.1f}")
