#!/usr/bin/env python3
for q in range(1, 40):
    for dollars in range(0, 25):
        for cents in range(0, 100):
            price = f"{dollars}.{cents:02d}"
            expected = q * (dollars * 100 + cents)
            got = int(q * float(price) * 100)
            if got != expected:
                print(q, price, got, expected)
                raise SystemExit(0)
print("NO_FAIL")
