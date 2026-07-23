# Payments Service - Test Repository

Sample repository for AuditMate testing. Contains transaction loading implementation with database link segregation.

## Structure

- `scheduler/` - Control-M job definitions
- `scripts/` - Shell scripts for job execution
- `db/oracle/` - Oracle PL/SQL packages

## Changes

- CHG-000123: Secure transaction load implementation
- JIRA-4521: Database link integration task

## References

See design_txn_load_dblink.md for architecture details.
