#!/usr/bin/env python3
"""
Test script for the XDG Benchmarking Dashboard
"""

import json
import os
import sys
from pathlib import Path

def test_data_structure():
    """Test that the data structure is valid"""
    print("Testing XDG Benchmarking Dashboard Data Structure...")

    # Check if results directory exists
    results_dir = Path("results/runs")
    if not results_dir.exists():
        print("❌ Error: results/runs directory not found")
        return False

    print(f"✅ Found results directory: {results_dir}")

    # Check each run
    valid_runs = 0
    for run_dir in results_dir.iterdir():
        if not run_dir.is_dir():
            continue

        run_id = run_dir.name
        config_file = run_dir / "config.json"
        results_file = run_dir / "results.json"

        print(f"\n📁 Testing run: {run_id}")

        # Check required files
        if not config_file.exists():
            print(f"❌ Missing config.json in {run_id}")
            continue
        if not results_file.exists():
            print(f"❌ Missing results.json in {run_id}")
            continue

        print(f"✅ Found config.json and results.json")

        # Validate JSON structure
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            with open(results_file, 'r') as f:
                results = json.load(f)

            # Basic validation
            if config['run_id'] != results['run_id']:
                print(f"❌ Run ID mismatch: {config['run_id']} vs {results['run_id']}")
                continue

            if config['date'] != results['date']:
                print(f"❌ Date mismatch: {config['date']} vs {results['date']}")
                continue

            print(f"✅ JSON structure valid")

            # Check models and executables
            config_models = set(config['models'])
            config_executables = set(config['executables'])
            results_models = set(results['results'].keys())

            # Check if all config models have results
            missing_models = config_models - results_models
            if missing_models:
                print(f"❌ Missing results for models: {missing_models}")
                continue

            print(f"✅ Models: {', '.join(config_models)}")
            print(f"✅ Executables: {', '.join(config_executables)}")

            # Check scaling data
            total_data_points = 0
            for model, model_results in results['results'].items():
                for executable, exec_results in model_results.items():
                    scaling_points = len(exec_results['scaling'])
                    total_data_points += scaling_points
                    print(f"   📊 {model}/{executable}: {scaling_points} scaling points")

            print(f"✅ Total data points: {total_data_points}")
            valid_runs += 1

        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
        except KeyError as e:
            print(f"❌ Missing required field: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

    print(f"\n📈 Summary: {valid_runs} valid runs found")
    return valid_runs > 0

def test_dashboard_import():
    """Test that the dashboard can be imported"""
    print("\nTesting Dashboard Import...")

    try:
        # Import the dashboard module
        sys.path.insert(0, '.')
        from dashboard import BenchmarkDataManager

        print("✅ Successfully imported BenchmarkDataManager")

        # Test data manager
        dm = BenchmarkDataManager()
        print(f"✅ Data manager initialized with {len(dm.runs)} runs")
        print(f"✅ Discovered models: {', '.join(dm.models)}")
        print(f"✅ Discovered executables: {', '.join(dm.executables)}")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 XDG Benchmarking Dashboard Test Suite")
    print("=" * 50)

    # Test data structure
    data_ok = test_data_structure()

    # Test dashboard import
    import_ok = test_dashboard_import()

    print("\n" + "=" * 50)
    if data_ok and import_ok:
        print("🎉 All tests passed! Dashboard is ready to run.")
        print("\nTo start the dashboard:")
        print("  python dashboard.py")
        print("\nTo view the embedding example:")
        print("  open embed_example.html")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)