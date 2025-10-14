import data_processor

def test_all_parameters():
    """Test all parameters to ensure they work with real Excel data"""
    print("🧪 Testing All Parameters with Real Excel Data")
    print("=" * 60)
    
    # Get all available parameters
    parameters = data_processor.get_all_parameters()
    print(f"📋 Available parameters: {parameters}")
    print()
    
    for param in parameters:
        print(f"📊 Testing parameter: {param}")
        try:
            data = data_processor.get_parameter_data(param)
            if data:
                print(f"  ✅ Success: {len(data)} batches found")
                print(f"  📈 Sample batches:")
                for i, batch in enumerate(data[:3]):  # Show first 3 batches
                    print(f"    {i+1}. {batch['batch']}: mean={batch['mean']}, count={batch['count']}")
                if len(data) > 3:
                    print(f"    ... and {len(data)-3} more batches")
            else:
                print(f"  ❌ No data found")
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
        print()

def test_complete_batch_coverage():
    """Test that all 10 batches appear in all parameters"""
    print("🔍 Testing Complete Batch Coverage")
    print("=" * 40)
    
    data = data_processor.extract_chart_data()
    
    for param, param_data in data.items():
        print(f"\n📊 {param}:")
        print(f"  Total batches: {len(param_data)}")
        batch_names = [batch['batch'] for batch in param_data]
        print(f"  Batch names: {batch_names}")
        
        # Show statistics for this parameter
        means = [batch['mean'] for batch in param_data]
        print(f"  Mean range: {min(means):.2f} to {max(means):.2f}")
        total_measurements = sum(batch['count'] for batch in param_data)
        print(f"  Total measurements: {total_measurements}")

if __name__ == "__main__":
    test_all_parameters()
    print("\n" + "="*60)
    test_complete_batch_coverage()