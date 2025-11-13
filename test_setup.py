"""
Test script to verify the setup
"""
import sys
import os

# Fix Windows console encoding
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def test_imports():
    """Test if all modules can be imported"""
    print("Testing module imports...")

    try:
        from modules import config, logger, database, stock_codes, stock_data, visualization
        print("✅ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_stock_codes():
    """Test stock codes module"""
    print("\nTesting stock codes...")

    try:
        from modules.stock_codes import get_stock_codes, get_stock_name
        codes = get_stock_codes()
        print(f"✅ Stock codes loaded: {len(codes)} stocks")
        print(f"   Sample: {codes[:5]}")

        # Test stock name lookup
        name = get_stock_name("AAPL")
        print(f"✅ Stock name lookup: AAPL = {name}")
        return True
    except Exception as e:
        print(f"❌ Stock codes test failed: {e}")
        return False

def test_config():
    """Test configuration"""
    print("\nTesting configuration...")

    try:
        from modules.config import DEBUG_MODE, TOP_K, LOOKBACK_DAYS, DB_PATH
        print(f"✅ Configuration loaded:")
        print(f"   DEBUG_MODE: {DEBUG_MODE}")
        print(f"   TOP_K: {TOP_K}")
        print(f"   LOOKBACK_DAYS: {LOOKBACK_DAYS}")
        print(f"   DB_PATH: {DB_PATH}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("US Stocks Autobot - Setup Test")
    print("=" * 60)

    tests = [
        test_imports,
        test_stock_codes,
        test_config,
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 60)
    if all(results):
        print("✅ All tests passed! Setup is complete.")
        print("\nYou can now run the main program:")
        print("  python main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
    print("=" * 60)

if __name__ == "__main__":
    main()
