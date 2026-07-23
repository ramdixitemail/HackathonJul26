# Runbook: Payments Recovery Procedures

**Last Updated**: 2026-06-01

## Overview

This runbook documents procedures for recovering failed payment transactions using database link verification.

## Prerequisites

- Access to SRC_DBLINK
- Database admin credentials
- Notification access for alerts

## Recovery Steps

### 1. Identify Failed Transactions

```sql
SELECT txn_id, error_message FROM txn_log
WHERE status = 'FAILED'
AND log_timestamp >= TRUNC(SYSDATE);
```

### 2. Verify Source Data

Check source database via SRC_DBLINK:

```sql
SELECT * FROM source_transactions@SRC_DBLINK
WHERE src_txn_id = <failed_txn_id>;
```

### 3. Retry Load

Run targeted re-load for specific transactions.

## Escalation

For critical issues, notify TXN-Team@company.com
