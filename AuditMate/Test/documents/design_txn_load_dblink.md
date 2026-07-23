# Design: Daily TXN Load via dbLink

**Document ID**: AUD-2026-0161  
**Related**: CHG-000123, JIRA-4521  
**Last Updated**: 2026-03-15

## Executive Summary

This design document outlines the implementation of secure daily transaction loading via Oracle database link (dbLink), ensuring data segregation and compliance with internal audit requirements.

## Architecture Overview

```
[Source DB] ---(SRC_DBLINK)--- [Target DB]
              (Read-Only)
                  |
                  v
          PKG_TXN_LOAD (read)
                  |
                  v
          Transaction Processing
                  |
                  v
          PKG_TXN_CTRL (COMMIT/ROLLBACK)
```

## Key Components

### 1. Database Link Configuration

- **Link Name**: SRC_DBLINK
- **Access**: Read-only via secure wallet
- **Defined in**: `db/oracle/PKG_TXN_LOAD.sql` (lines 17-23)

### 2. Source Data Access

All transaction data must flow through SRC_DBLINK:

```sql
SELECT src_txn_id, src_amount, src_customer_id
FROM source_transactions@SRC_DBLINK  -- Read-only segregation
```

Customer enrichment also via link:

```sql
FROM src_customer@SRC_DBLINK  -- PKG_TXN_ENRICH.sql
```

### 3. Transaction Control

Proper COMMIT/ROLLBACK handling:
- **Commit**: When batch successfully loads (line 25 of PKG_TXN_CTRL.sql)
- **Rollback**: On error or empty batch (line 26 of PKG_TXN_CTRL.sql)

### 4. Scheduler

Control-M job triggers nightly:
- **File**: `scheduler/LOAD_TN_DAILY.xml`
- **Command**: `scripts/load_txn.sh`
- **Schedule**: 02:00 UTC daily

## Compliance Controls

✓ Data segregation via read-only dbLink  
✓ Proper transaction control with rollback protection  
✓ Audit logging in transaction log  
✓ Four-eyes approval (CHG-000123: a_rao, s_kaur)  
✓ Automated scheduling with monitoring  

## Diagram

See `diagrams/txn_flow.svg` for detailed data flow diagram.

## References

- CHG-000123: Change request for implementation
- JIRA-4521: Original requirements specification
- PR #141: Implementation pull request (approved by A.Rao, S.Kaur)
