"""
Quick test script - Test with only 10 stocks
"""
import sys
import os

# Fix Windows console encoding
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Override stock codes for quick test
os.environ['US_STOCK_CODES'] = 'AAPL,MSFT,GOOGL,AMZN,NVDA,TSLA,META,JPM,JNJ,V'
os.environ['LOOKBACK_DAYS'] = '60'

print("=" * 60)
print("🧪 Quick Test - Testing with 10 stocks only")
print("=" * 60)

# Import and run main
from main import main

try:
    main()
    print("\n✅ Quick test completed successfully!")
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
