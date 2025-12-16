import streamlit as st
import pyodbc
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Secure Banking System", page_icon="🏦", layout="wide")

# --- DATABASE CONNECTION ---
# ⚠️ CHANGE 'SERVER' to your actual SQL Server Name (e.g., DESKTOP-XXXX\SQLEXPRESS or localhost)
def get_connection():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=SHAHZAIBLATIF\SQLEXPRESS;'  
        'DATABASE=BankingDB;'
        'Trusted_Connection=yes;'
    )

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["💸 Transfer Funds", "📜 Audit Logs", "🛡️ Admin / Schema Logs"])

# --- PAGE 1: TRANSFER FUNDS ---
if page == "💸 Transfer Funds":
    st.title("💸 Money Transfer")
    st.markdown("Use this form to safely transfer money using **ACID Transactions**.")

    col1, col2 = st.columns(2)
    with col1:
        sender_id = st.number_input("Sender Account ID", min_value=1, step=1)
        amount = st.number_input("Amount to Transfer ($)", min_value=1.0, step=10.0)
    with col2:
        receiver_id = st.number_input("Receiver Account ID", min_value=1, step=1)

    if st.button("🚀 Transfer Now"):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Call the Stored Procedure we created earlier
            # Syntax: EXEC sp_TransferFunds @SenderID, @ReceiverID, @Amount
            cursor.execute("{CALL sp_TransferFunds (?, ?, ?)}", (sender_id, receiver_id, amount))
            conn.commit()
            
            st.success("✅ Transfer Successful! Transaction Committed.")
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Transfer Failed: {e}")
            st.warning("Transaction has been Rolled Back automatically.")
        finally:
            if 'conn' in locals(): conn.close()

    # Show Current Accounts for Reference
    st.subheader("📊 Live Account Balances")
    try:
        conn = get_connection()
        df = pd.read_sql("SELECT AccountID, CustomerID, AccountType, Balance FROM Accounts", conn)
        st.dataframe(df, use_container_width=True)
    except:
        st.info("Could not load balances. Check your database connection.")

# --- PAGE 2: AUDIT LOGS ---
elif page == "📜 Audit Logs":
    st.title("📜 Audit Trail (DML Triggers)")
    st.markdown("This log is automatically populated by the **`trg_AuditAccountBalance`** trigger whenever a balance changes.")

    if st.button("🔄 Refresh Logs"):
        st.rerun()

    try:
        conn = get_connection()
        # Query the Audit Table
        df = pd.read_sql("SELECT * FROM AccountAuditLog ORDER BY ChangeDate DESC", conn)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading logs: {e}")

# --- PAGE 3: SCHEMA LOGS ---
elif page == "🛡️ Admin / Schema Logs":
    st.title("🛡️ Security Logs (DDL Triggers)")
    st.markdown("This tracks structural changes (CREATE/DROP) captured by **`trg_LogSchemaChanges`**.")

    try:
        conn = get_connection()
        df = pd.read_sql("SELECT * FROM SchemaChangeLog ORDER BY EventDate DESC", conn)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading schema logs: {e}")