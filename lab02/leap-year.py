year = int(input("Enter a year: "))
leapYear = None
if year % 400 == 0:
    leapYear = True
elif year % 100 == 0:
    leapYear = False
elif year % 4 == 0:
    leapYear = True
else:
    leapYear = False
leapYearStr = ''
if not leapYear:
    leapYearStr = 'not '
print(f"The year {year} is {leapYearStr}a leap year.")
