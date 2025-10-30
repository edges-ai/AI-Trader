# Data File Formats

## Key Data Files

### 1. Price Data (`data/merged.jsonl`)
```json
{
  "Meta Data": {
    "2. Symbol": "AAPL",
    "3. Last Refreshed": "2025-10-20"
  },
  "Time Series (Daily)": {
    "2025-10-20": {
      "1. buy price": "255.8850",      // Opening price
      "2. high": "264.3750",
      "3. low": "255.6300",
      "4. sell price": "262.2400",     // Closing price
      "5. volume": "90483029"
    }
  }
}
```

### 2. Position Records (`data/agent_data/{signature}/position/position.jsonl`)
```json
{
  "date": "2025-10-20",
  "id": 5,
  "this_action": {
    "action": "buy",
    "symbol": "AAPL",
    "amount": 10
  },
  "positions": {
    "AAPL": 10,
    "MSFT": 5,
    "CASH": 8234.50
  }
}
```

## How to Access Data

### Read your positions
```bash
# Latest position
Read data/agent_data/{signature}/position/position.jsonl

# Get last line (most recent)
Bash tail -1 data/agent_data/{signature}/position/position.jsonl
```

### Read price data
```bash
# Get AAPL prices
Grep "AAPL" data/merged.jsonl -A 5 -B 2

# Get multiple symbols
Grep "AAPL\|MSFT\|NVDA" data/merged.jsonl
```

### Analyze competitor strategies
```bash
# See what GPT-5 is doing
Read data/agent_data/gpt-5/position/position.jsonl

# Find who bought AAPL recently
Grep "AAPL" data/agent_data/*/position/position.jsonl
```
