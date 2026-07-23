-- Data enrichment via database link
-- Reads customer data from SRC_DBLINK

CREATE OR REPLACE PACKAGE PKG_TXN_ENRICH AS
  PROCEDURE enrich_transactions;
END PKG_TXN_ENRICH;
/

CREATE OR REPLACE PACKAGE BODY PKG_TXN_ENRICH AS
  
  PROCEDURE enrich_transactions AS
  BEGIN
    -- All customer data must come via SRC_DBLINK for segregation
    UPDATE transactions t
    SET customer_name = (
      SELECT src_customer_name
      FROM src_customer@SRC_DBLINK
      WHERE customer_id = t.customer_id
    )
    WHERE customer_name IS NULL;
    
    COMMIT;
  EXCEPTION
    WHEN OTHERS THEN
      ROLLBACK;
      RAISE;
  END;
  
END PKG_TXN_ENRICH;
/
