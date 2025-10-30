# Decision Output Format

**CRITICAL**: You MUST output your decision in this EXACT format:

```
<DECISION>
{
  "action": "buy",
  "symbol": "AAPL",
  "amount": 10,
  "confidence": 0.85,
  "reasoning": "Strong momentum + diversification benefit + competitive edge vs other agents"
}
</DECISION>
```

## Field Requirements

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| **action** | string | "buy", "sell", "hold" | Trade action (required) |
| **symbol** | string | NASDAQ 100 ticker | Stock symbol (empty for hold) |
| **amount** | integer | > 0 | Number of shares (0 for hold) |
| **confidence** | float | 0.0 to 1.0 | Your conviction level |
| **reasoning** | string | 1-3 sentences | Brief explanation |

## Example Decisions

### Example 1: Buy Decision
```json
{
  "action": "buy",
  "symbol": "NVDA",
  "amount": 5,
  "confidence": 0.82,
  "reasoning": "Strong momentum (SMA5 > SMA20), positive earnings outlook, low correlation with existing positions (AAPL, MSFT). Technical analysis shows bullish trend continuation."
}
```

### Example 2: Sell Decision
```json
{
  "action": "sell",
  "symbol": "AAPL",
  "amount": 5,
  "confidence": 0.75,
  "reasoning": "Portfolio over-concentrated in tech (AAPL+MSFT = 70%). Taking partial profits after 8% gain. Preserving capital for diversification opportunity."
}
```

### Example 3: Hold Decision
```json
{
  "action": "hold",
  "symbol": "",
  "amount": 0,
  "confidence": 0.60,
  "reasoning": "Market conditions unclear, mixed technical signals. No compelling entry points. Maintaining current positions while monitoring COST for potential entry."
}
```
