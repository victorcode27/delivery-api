import database

# Direct database test
print("=" * 60)
print("DIRECT DATABASE TEST")
print("=" * 60)

# Test with exact parameters
date_from = '2026-01-29'
date_to = '2026-01-29'

print(f"Calling database.get_dispatched_invoices(")
print(f"  date_from='{date_from}',")
print(f"  date_to='{date_to}',")
print(f"  filter_type='dispatch'")
print(f")")
print()

results, total = database.get_dispatched_invoices(
    date_from=date_from,
    date_to=date_to,
    filter_type='dispatch'
)

print(f"Results: {len(results)} invoices")
print(f"Total: {total}")
print()

if results:
    print("First invoice:")
    for key, value in results[0].items():
        print(f"  {key}: {value}")
