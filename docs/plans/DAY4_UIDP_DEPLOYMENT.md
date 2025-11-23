# Day 4: UIDP Deployment Guide

**Objective**: Deploy and test the UIDP (Unified Income Distribution Protocol) system with webhook integration, NFT minting, and 7% charity routing.

---

## Overview

This guide implements the core UIDP infrastructure that automatically:
1. Receives revenue notifications from payment processors
2. Calculates 7% charitable allocation
3. Executes transfers to ValorYield Engine
4. Generates NFT transaction receipts
5. Logs all transactions with cryptographic verification

---

## Components Created

### 1. Enhanced UIDP Executor (`uidp_executor_enhanced.py`)
Core business logic for charitable distribution:
- Automatic 7% allocation calculation
- Transaction logging to `dao_treasury_log.json`
- NFT receipt generation
- SHA-256 verification hashes
- Statistics and reporting

### 2. Webhook Integration Server (`uidp_webhook_server.py`)
Flask-based server receiving webhooks from:
- Stripe (payment_intent.succeeded, charge.succeeded)
- PayPal (PAYMENT.CAPTURE.COMPLETED)
- Cryptocurrency payment processors
- Manual API endpoint for testing

### 3. Configuration File (`uidp_config.json`)
Contains entity information and beneficiary allocations

---

## Installation

### Prerequisites
```bash
# Python 3.8+ required
python3 --version

# Install dependencies
pip install flask
# For production: pip install stripe paypal-checkout-sdk
```

### Setup
```bash
cd /home/runner/work/Strategickhaos-DAO_Compliance/Strategickhaos-DAO_Compliance

# Make scripts executable
chmod +x uidp_executor_enhanced.py
chmod +x uidp_webhook_server.py

# Create necessary directories
mkdir -p nft_receipts
mkdir -p webhook_logs

# Test UIDP executor
python3 uidp_executor_enhanced.py
```

---

## Configuration

### UIDP Config (`uidp_config.json`)

The executor automatically creates a default configuration file. Customize as needed:

```json
{
  "for_profit_entity": {
    "name": "Strategickhaos DAO LLC",
    "ein": "39-2900295",
    "bank_account": "[REDACTED - Configure in production]"
  },
  "charity_entity": {
    "name": "ValorYield Engine",
    "ein": "39-2923503",
    "bank_account": "[REDACTED - Configure in production]"
  },
  "beneficiaries": [
    {"name": "St. Jude Children's Research Hospital", "allocation": 0.25},
    {"name": "Médecins Sans Frontières", "allocation": 0.20},
    {"name": "Veterans Programs", "allocation": 0.40},
    {"name": "Educational Institutions", "allocation": 0.15}
  ]
}
```

### Environment Variables

For production deployment, set these environment variables:

```bash
# Stripe webhook secret (from Stripe dashboard)
export STRIPE_WEBHOOK_SECRET="whsec_your_secret_here"

# PayPal webhook ID (from PayPal developer dashboard)
export PAYPAL_WEBHOOK_ID="your_webhook_id_here"

# Optional: Database connection for production
export DATABASE_URL="postgresql://..."
```

---

## Testing the UIDP Executor

### Test 1: Run Standalone Executor

```bash
# Execute test transactions
python3 uidp_executor_enhanced.py
```

Expected output:
```
============================================================
UIDP Executor - Test Run
============================================================

--- Processing Transaction: $1000.0 via stripe ---
[UIDP EXECUTOR] Transaction logged to dao_treasury_log.json
[UIDP EXECUTOR] [SIMULATED] Transfer of $70.00 to charity account
[UIDP EXECUTOR] NOTE: In production, actual bank transfer would execute here
[UIDP EXECUTOR] NFT receipt generated: nft_receipts/uidp_receipt_uidp-20251123-xxxxx.json
[UIDP EXECUTOR] Successfully allocated $70.00 to charity
[UIDP EXECUTOR] Transaction ID: uidp-20251123-xxxxx
[UIDP EXECUTOR] Verification Hash: abc123...

============================================================
STATISTICS
============================================================
total_transactions: 3
total_revenue: 1750.0
total_charity_allocation: 122.5
average_transaction: 583.33
effective_charity_percentage: 7.0
```

### Test 2: Verify Log File

```bash
# Check transaction log
cat dao_treasury_log.json | python3 -m json.tool
```

Should show structured transaction records with:
- UIDP transaction IDs
- Timestamps
- Allocation amounts
- Entity information
- Payment processor details

### Test 3: Verify NFT Receipts

```bash
# List generated NFT receipts
ls -lh nft_receipts/

# View a receipt
cat nft_receipts/uidp_receipt_*.json | python3 -m json.tool
```

Each NFT contains:
- Transaction metadata
- Allocation amounts
- Entity information
- Attributes for NFT platforms

---

## Testing Webhook Server

### Start the Server

```bash
# Start webhook server
python3 uidp_webhook_server.py
```

Expected output:
```
============================================================
UIDP Webhook Integration Server
============================================================
Listening for webhooks from:
  - Stripe: /webhook/stripe
  - PayPal: /webhook/paypal
  - Crypto: /webhook/crypto
  - Manual: /api/process

API Endpoints:
  - Statistics: /api/statistics
  - Transactions: /api/transactions
  - Health: /health
============================================================

Starting server on http://localhost:5001
```

### Test 1: Health Check

```bash
# In a new terminal
curl http://localhost:5001/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "UIDP Webhook Server",
  "timestamp": "2025-11-23T12:00:00Z"
}
```

### Test 2: Manual Transaction Processing

```bash
# Simulate a $100 donation
curl -X POST http://localhost:5001/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100.00,
    "processor": "test",
    "transaction_id": "test_001",
    "metadata": {
      "test": true,
      "donor": "Test Donor"
    }
  }'
```

Expected response:
```json
{
  "success": true,
  "uidp_transaction_id": "uidp-20251123-xxxxx",
  "allocation": {
    "total_revenue": 100.0,
    "charity_allocation": 7.0,
    "for_profit_retention": 93.0,
    "charity_percentage": 7.0
  },
  "transfer": {
    "status": "simulated",
    "amount": 7.0,
    "message": "[SIMULATED] Transfer of $7.00 to charity account"
  },
  "nft_receipt": {
    "filename": "nft_receipts/uidp_receipt_uidp-20251123-xxxxx.json"
  },
  "verification_hash": "abc123...",
  "message": "Successfully allocated $7.00 to charity"
}
```

### Test 3: Simulate Stripe Webhook

```bash
# Simulate Stripe payment_intent.succeeded event
curl -X POST http://localhost:5001/webhook/stripe \
  -H "Content-Type: application/json" \
  -d '{
    "id": "evt_test_123",
    "type": "payment_intent.succeeded",
    "data": {
      "object": {
        "id": "pi_test_123",
        "amount": 5000,
        "currency": "usd",
        "description": "Test donation"
      }
    }
  }'
```

Expected response:
```json
{
  "received": true,
  "uidp_result": {
    "transaction_id": "uidp-20251123-xxxxx",
    "charity_allocation": 3.5,
    "verification_hash": "abc123..."
  }
}
```

### Test 4: Simulate PayPal Webhook

```bash
# Simulate PayPal PAYMENT.CAPTURE.COMPLETED event
curl -X POST http://localhost:5001/webhook/paypal \
  -H "Content-Type: application/json" \
  -d '{
    "id": "WH-test123",
    "event_type": "PAYMENT.CAPTURE.COMPLETED",
    "resource": {
      "id": "CAPTURE-test123",
      "amount": {
        "value": "75.00",
        "currency_code": "USD"
      },
      "payer": {
        "email_address": "donor@example.com"
      }
    }
  }'
```

### Test 5: Get Statistics

```bash
# Retrieve UIDP statistics
curl http://localhost:5001/api/statistics
```

Expected response:
```json
{
  "total_transactions": 5,
  "total_revenue": 275.0,
  "total_charity_allocation": 19.25,
  "average_transaction": 55.0,
  "effective_charity_percentage": 7.0
}
```

### Test 6: Get Transaction History

```bash
# Retrieve last 5 transactions
curl http://localhost:5001/api/transactions?limit=5
```

---

## Webhook Logs

All webhook events are logged for debugging:

```bash
# View webhook logs
ls -lh webhook_logs/

# View a specific log
cat webhook_logs/stripe_webhook_20251123_120000.json | python3 -m json.tool
```

---

## NFT Minting (Advanced)

### Prepare NFT for Minting

Each transaction generates NFT metadata. To mint on-chain:

```bash
# Upload NFT metadata to IPFS
ipfs add nft_receipts/uidp_receipt_uidp-20251123-xxxxx.json
# Returns: QmXYZ123... (use this as metadata URI)

# Mint using existing smart contract
# (Requires Web3.py or ethers.js - see scripts/mint_uidp.js)
```

---

## Production Deployment Checklist

### Prerequisites
- [ ] Stripe account created and verified
- [ ] PayPal business account created
- [ ] Bank accounts configured for both entities
- [ ] SSL certificate for webhook endpoint
- [ ] Production server (not localhost)

### Security
- [ ] Environment variables configured (not hardcoded)
- [ ] Webhook signature verification enabled
- [ ] HTTPS enforced for all webhook endpoints
- [ ] Rate limiting implemented
- [ ] Database configured (not JSON files)
- [ ] Backup system for transaction logs
- [ ] Monitoring and alerts configured

### Stripe Setup
1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://your-domain.com/webhook/stripe`
3. Select events to listen for:
   - `payment_intent.succeeded`
   - `charge.succeeded`
4. Copy webhook signing secret to environment variable
5. Test with Stripe CLI: `stripe listen --forward-to localhost:5001/webhook/stripe`

### PayPal Setup
1. Go to PayPal Developer Dashboard → Webhooks
2. Add webhook: `https://your-domain.com/webhook/paypal`
3. Select event types:
   - `PAYMENT.CAPTURE.COMPLETED`
4. Copy webhook ID to environment variable
5. Test with PayPal sandbox

### Bank Integration
1. Set up bank API credentials (ACH transfer or wire)
2. Configure accounts in `uidp_config.json`
3. Replace simulated transfers with actual bank API calls
4. Test with small amounts ($0.01) first
5. Implement transaction reconciliation

### Monitoring
```bash
# Set up log monitoring
tail -f webhook_logs/*.json

# Monitor transaction log
watch -n 5 'cat dao_treasury_log.json | python3 -m json.tool | tail -20'

# Check statistics periodically
watch -n 60 'curl -s http://localhost:5001/api/statistics | python3 -m json.tool'
```

---

## Integration with Existing Components

### Link to Transparency Reporting (Day 6)

The `dao_treasury_log.json` file will be used in Day 6 for transparency reports.

### Link to OpenTimestamps (Day 5)

Transaction logs will be timestamped using OpenTimestamps:
```bash
# After each transaction batch
ots stamp dao_treasury_log.json
git add dao_treasury_log.json.ots
git commit -m "Add OpenTimestamps proof for transactions"
```

### Link to Git Workflow

```bash
# After processing transactions, commit to Git
git add dao_treasury_log.json nft_receipts/
git commit -m "Process UIDP transactions: [date]"
git push
```

---

## Troubleshooting

### Issue: Webhook not received

**Check**:
1. Server running? `curl http://localhost:5001/health`
2. Firewall blocking port 5001?
3. Webhook URL correct in payment processor dashboard?
4. Using HTTPS in production? (Stripe/PayPal require HTTPS)

**Solution**: Use ngrok for testing: `ngrok http 5001`

### Issue: Signature verification fails

**Check**:
1. Webhook secret correct?
2. Environment variable set?
3. Payload modified in transit?

**Solution**: Log raw payload and signature for debugging

### Issue: Transaction not logging

**Check**:
1. File permissions for `dao_treasury_log.json`?
2. Disk space available?
3. JSON formatting errors?

**Solution**: Check logs, verify write permissions

### Issue: NFT metadata not generating

**Check**:
1. `nft_receipts/` directory exists?
2. Write permissions?

**Solution**: `mkdir -p nft_receipts && chmod 755 nft_receipts`

---

## Testing Script

Create a comprehensive test:

```bash
#!/bin/bash
# test_uidp_deployment.sh

echo "Testing UIDP Deployment..."

# Test 1: Executor standalone
echo "Test 1: Running UIDP executor..."
python3 uidp_executor_enhanced.py
if [ $? -eq 0 ]; then
    echo "✓ Executor test passed"
else
    echo "✗ Executor test failed"
    exit 1
fi

# Start webhook server in background
echo "Test 2: Starting webhook server..."
python3 uidp_webhook_server.py &
SERVER_PID=$!
sleep 3

# Test health endpoint
echo "Test 3: Health check..."
curl -f http://localhost:5001/health
if [ $? -eq 0 ]; then
    echo "✓ Health check passed"
else
    echo "✗ Health check failed"
    kill $SERVER_PID
    exit 1
fi

# Test manual processing
echo "Test 4: Manual transaction processing..."
curl -X POST http://localhost:5001/api/process \
  -H "Content-Type: application/json" \
  -d '{"amount": 100, "processor": "test"}' \
  -f
if [ $? -eq 0 ]; then
    echo "✓ Manual processing passed"
else
    echo "✗ Manual processing failed"
    kill $SERVER_PID
    exit 1
fi

# Test statistics
echo "Test 5: Statistics endpoint..."
curl -f http://localhost:5001/api/statistics
if [ $? -eq 0 ]; then
    echo "✓ Statistics passed"
else
    echo "✗ Statistics failed"
    kill $SERVER_PID
    exit 1
fi

# Cleanup
kill $SERVER_PID

echo ""
echo "All tests passed! ✓"
echo "Files created:"
ls -lh dao_treasury_log.json nft_receipts/*.json 2>/dev/null
```

Make it executable and run:
```bash
chmod +x test_uidp_deployment.sh
./test_uidp_deployment.sh
```

---

## Success Criteria

Day 4 is complete when:

- [x] UIDP executor processes transactions correctly
- [x] 7% allocation calculated accurately
- [x] Transactions logged to `dao_treasury_log.json`
- [x] NFT receipts generated with metadata
- [x] Webhook server receives and processes events
- [x] Statistics and reporting working
- [x] All tests pass
- [x] Documentation complete

---

## Next Steps (Day 5)

Tomorrow we'll add cryptographic verification:
1. GPG signing of transaction logs
2. OpenTimestamps blockchain proofs
3. IPFS upload for NFT metadata
4. Arweave permanent storage

All the infrastructure is now in place for that integration.

---

## Files Created

```
├── uidp_executor_enhanced.py       # Core UIDP logic
├── uidp_webhook_server.py          # Webhook integration
├── uidp_config.json                # Configuration (auto-created)
├── dao_treasury_log.json           # Transaction log (auto-created)
├── nft_receipts/                   # NFT metadata (auto-created)
│   └── uidp_receipt_*.json
└── webhook_logs/                   # Webhook event logs (auto-created)
    ├── stripe_webhook_*.json
    └── paypal_webhook_*.json
```

---

*This guide completes Day 4 of the 7-day implementation roadmap.*

*Document Version: 1.0*  
*Last Updated: November 23, 2025*  
*Status: Ready for testing and deployment*
