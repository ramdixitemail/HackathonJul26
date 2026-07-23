#!/bin/bash
# Transaction load script
# JIRA-4521 entrypoint

set -e
LOG_FILE="/var/log/txn_load.log"

echo "Starting transaction load at $(date)" >> $LOG_FILE

# Connect to database and execute load procedure
sqlplus -s <<EOF >> $LOG_FILE 2>&1
SET ECHO OFF
SET VERIFY OFF
SET PAGESIZE 0
SET FEEDBACK OFF
SET ECHO ON
SET DEFINE ON

@db/oracle/PKG_TXN_LOAD.sql

-- Call load_txn procedure
DECLARE
  v_rc INTEGER;
BEGIN
  PKG_TXN_LOAD.load_txn(v_rc);
  DBMS_OUTPUT.PUT_LINE('Load completed with return code: ' || v_rc);
END;
/

EXIT SQL.SQLCODE
EOF

LOAD_RC=$?

echo "Transaction load completed with rc=$LOAD_RC at $(date)" >> $LOG_FILE
exit $LOAD_RC
