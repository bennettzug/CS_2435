import bisect

income = int(
    input(
        "This program computes taxes for the year 2022 for singles.\nEnter taxable income: "
    )
)
cutoffs = [7800, 39000, 75000, 185725, 305500, 475000, 603875]
rates = [0.10, 0.13, 0.16, 0.20, 0.22, 0.25, 0.34, 0.36]


def taxesOwed(cutoffs: list, rates: list, income: int):
    rate = rates[bisect.bisect_left(cutoffs, income)]
    return rate * income


UserTaxesOwed = taxesOwed(cutoffs, rates, income)

print(f"Total tax owed is {UserTaxesOwed:.2f}")
