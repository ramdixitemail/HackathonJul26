-- Transaction Control Package
-- Handles COMMIT/ROLLBACK with proper exception handling

CREATE OR REPLACE PACKAGE PKG_TXN_CTRL AS
  PROCEDURE commit_batch(p_row_count IN INTEGER, p_return_code OUT INTEGER);
END PKG_TXN_CTRL;
/

CREATE OR REPLACE PACKAGE BODY PKG_TXN_CTRL AS
  
  PROCEDURE commit_batch(p_row_count IN INTEGER, p_return_code OUT INTEGER) AS
  BEGIN
    IF p_row_count > 0 THEN
      COMMIT;  -- Transaction control: COMMIT successful batch
      p_return_code := 0;
      DBMS_OUTPUT.PUT_LINE('Batch committed: ' || p_row_count || ' rows');
    ELSE
      ROLLBACK;  -- Transaction control: ROLLBACK empty batch
      p_return_code := 1;
      DBMS_OUTPUT.PUT_LINE('Batch rolled back: no rows');
    END IF;
  EXCEPTION
    WHEN OTHERS THEN
      ROLLBACK;  -- Transaction control: ROLLBACK on any error
      p_return_code := SQLCODE;
      DBMS_OUTPUT.PUT_LINE('Error in commit_batch: ' || SQLERRM);
  END;
  
END PKG_TXN_CTRL;
/
