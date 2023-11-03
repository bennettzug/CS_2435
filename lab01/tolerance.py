desired_weight = int(input("Enter desired weight: "))
tolerance = int(input("Enter tolerance (as percentage): ")) * 0.01
min_weight = desired_weight - tolerance * desired_weight
max_weight = desired_weight + tolerance * desired_weight
print(
    f"The range of accepted weight for the part is from {min_weight:.1f} to {max_weight:.1f}"
)
