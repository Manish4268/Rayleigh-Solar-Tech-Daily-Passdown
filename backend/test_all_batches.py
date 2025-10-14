import data_processor

# Get all batch data
data = data_processor.extract_chart_data()
pce_data = data['PCE']

print("All PCE batch data:")
print(f"Total batches: {len(pce_data)}")
print()

for i, batch in enumerate(pce_data, 1):
    print(f"{i:2d}. {batch['batch']}: mean={batch['mean']:6.2f}%, count={batch['count']:3d} measurements")