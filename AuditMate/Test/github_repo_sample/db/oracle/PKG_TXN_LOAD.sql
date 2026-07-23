-- Transaction Load Package
-- This package handles daily transaction loading via database link
-- Related: CHG-000123, JIRA-4521

CREATE OR REPLACE PACKAGE PKG_TXN_LOAD AS
  PROCEDURE load_txn(p_return_code OUT INTEGER);
  PROCEDURE log_transaction(p_txn_id NUMBER, p_status VARCHAR2);
END PKG_TXN_LOAD;
/

CREATE OR REPLACE PACKAGE BODY PKG_TXN_LOAD AS
  
  -- Create database link for secure data access
  -- All reads must go through this link (read-only)
  -- Note: Link password stored in secure wallet
  
  PROCEDURE setup_dblink AS
  BEGIN
    EXECUTE IMMEDIATE 'CREATE DATABASE LINK SRC_DBLINK ' ||
      'CONNECT TO srcuser IDENTIFIED BY "password" ' ||
      'USING ''(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)' ||
      '(HOST=source.db.company.com)(PORT=1521)))(CONNECT_DATA=(SERVICE_NAME=SRCDB)))''';
  EXCEPTION
    WHEN OTHERS THEN
      IF SQLCODE != -2120 THEN -- Link already exists
        RAISE;
      END IF;
  END;
  
  PROCEDURE load_txn(p_return_code OUT INTEGER) AS
    v_count INTEGER := 0;
  BEGIN
    setup_dblink;
    
    -- Read source transactions via SRC_DBLINK (read-only segregation)
    INSERT INTO transactions (txn_id, amount, customer_id, txn_date)
    SELECT src_txn_id, src_amount, src_customer_id, src_txn_date
    FROM source_transactions@SRC_DBLINK
    WHERE load_date = TRUNC(SYSDATE);
    
    v_count := SQL%ROWCOUNT;
    
    -- Call transaction control procedure
    PKG_TXN_CTRL.commit_batch(v_count, p_return_code);
    
    DBMS_OUTPUT.PUT_LINE('Loaded ' || v_count || ' transactions');
    
  EXCEPTION
    WHEN OTHERS THEN
      p_return_code := SQLCODE;
      DBMS_OUTPUT.PUT_LINE('Error: ' || SQLERRM);
      ROLLBACK;
  END;
  
  PROCEDURE log_transaction(p_txn_id NUMBER, p_status VARCHAR2) AS
  BEGIN
    INSERT INTO txn_log (txn_id, status, log_timestamp)
    VALUES (p_txn_id, p_status, SYSDATE);
  END;
  
END PKG_TXN_LOAD;
/
