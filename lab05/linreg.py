f = open("weather-data.txt")

print("This program computes the linear regression of "
      "weather data starting in 1900")

data = []
for line in f:
    parts = line.split(" ")
    year = int(parts[0]) - 1900
    temp = float(parts[1])
    info = (year, temp)
    data.append(info)

f.close()

x_avg = 0
y_avg = 0
for year, temp in data:
    x_avg += year
    y_avg += temp

x_avg /= len(data)
y_avg /= len(data)


numerator = 0
denominator = 0
for year, temp in data:
    numerator += (year - x_avg) * (temp - y_avg)
    denominator += (year - x_avg) ** 2

m = numerator / denominator

c = y_avg - m * x_avg

print(f"m = {m:.6f}")
print(f"c = {c:.6f}")
