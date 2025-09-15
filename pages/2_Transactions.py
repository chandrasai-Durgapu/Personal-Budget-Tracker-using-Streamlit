import streamlit as st
import pandas as pd
import datetime
import io

from setup.db import (
    get_user_categories,
    add_transaction,
    update_transaction,
    delete_transaction,
    fetch_transaction_history
)

# --- Callbacks for database operations ---
def add_transaction_callback():
    amount = st.session_state.add_trans_amount
    date = st.session_state.add_trans_date
    category_id = st.session_state.add_trans_cat
    note = st.session_state.add_trans_note
    
    if amount <= 0:
        st.error("Amount must be positive.")
    else:
        add_transaction(st.session_state.user_id, category_id, amount, date.strftime("%Y-%m-%d"), note)
        st.success("Transaction added successfully!")

def update_transactions_callback(edited_df):
    for _, row in edited_df.iterrows():
        try:
            category_id = get_category_id_from_name(st.session_state.user_id, row['Category'])
            date_str = row['Date'].strftime("%Y-%m-%d")
            update_transaction(row['ID'], category_id, row['Amount'], date_str, row['Note'])
        except Exception as e:
            st.error(f"Failed to update transaction {row['ID']}: {e}")
    st.success("Transactions updated successfully!")

def delete_transaction_callback():
    trans_id_to_del = st.session_state.trans_select_del
    delete_transaction(trans_id_to_del)
    st.success("Transaction deleted.")

# --- Helper function to get category ID ---
def get_category_id_from_name(user_id, category_name):
    categories = get_user_categories(user_id)
    for cat in categories:
        if cat[1] == category_name:
            return cat[0]
    return None

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access your Transactions.")
else:
    st.header("Transactions")

    categories = get_user_categories(st.session_state.user_id)
    if not categories:
        st.warning("Please add some categories in the 'Manage Categories' page before adding transactions.")
    else:
        categories_df = pd.DataFrame(categories, columns=['ID', 'Category Name', 'Category Type'])
        category_map = categories_df.set_index('ID')['Category Name'].to_dict()
    
        # --- Add New Transaction Form ---
        with st.container():
            st.subheader("Add New Transaction")
            with st.form('transaction_form', clear_on_submit=True):
                category_id = st.selectbox('Category', options=list(category_map.keys()), format_func=lambda x: category_map[x], key='add_trans_cat')
                amount = st.number_input('Amount', min_value=0.0, format="%.2f", key='add_trans_amount')
                date = st.date_input('Date', value=datetime.date.today(), key='add_trans_date')
                note = st.text_input('Note (optional)', key='add_trans_note')
                
                submitted = st.form_submit_button('Add Transaction', on_click=add_transaction_callback)

        # --- Transaction History with Editing ---
        with st.container():
            st.subheader("Transaction History")
            col_date1, col_date2 = st.columns(2)
            today = datetime.date.today()
            start_date = col_date1.date_input('Start Date', value=today - datetime.timedelta(days=30), key='trans_start')
            end_date = col_date2.date_input('End Date', value=today, key='trans_end')
            
            if start_date > end_date:
                st.error("Start date cannot be after end date.")
            else:
                transactions = fetch_transaction_history(st.session_state.user_id, start_date.strftime("%Y-%m-%d"), (end_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
                
                if transactions:
                    df = pd.DataFrame(transactions, columns=['ID', 'Date', 'Category', 'Type', 'Amount', 'Note'])
                    # ADD THIS LINE TO FIX THE ERROR
                    df['Date'] = pd.to_datetime(df['Date'])
                    editable_df = st.data_editor(df,
                                                 width='stretch',
                                                 hide_index=True,
                                                 key="transaction_editor",
                                                 column_config={
                                                     "ID": None,
                                                     "Category": st.column_config.SelectboxColumn(
                                                         "Category",
                                                         help="Select the category",
                                                         options=categories_df['Category Name'].tolist(),
                                                         required=True,
                                                     ),
                                                     "Type": st.column_config.SelectboxColumn(
                                                         "Type",
                                                         help="Transaction type",
                                                         options=categories_df['Category Type'].unique().tolist(),
                                                         required=True,
                                                     ),
                                                     "Date": st.column_config.DateColumn(
                                                         "Date",
                                                         help="Date of transaction",
                                                         format="YYYY-MM-DD",
                                                         min_value=datetime.date(2000, 1, 1),
                                                         max_value=datetime.date.today(),
                                                         required=True,
                                                     ),
                                                     "Amount": st.column_config.NumberColumn(
                                                         "Amount (₹)",
                                                         help="The transaction amount",
                                                         format="%.2f",
                                                         min_value=0.01,
                                                         required=True
                                                     ),
                                                     "Note": st.column_config.TextColumn("Note")
                                                 })

                    st.button("Save Changes to Transactions", on_click=update_transactions_callback, args=(editable_df,), width='stretch')
        
                    st.download_button(
                        label="Download Transaction History as CSV",
                        data=io.StringIO(df.to_csv(index=False)).getvalue(),
                        file_name=f"transactions_{start_date}_to_{end_date}.csv",
                        mime="text/csv",
                        width='stretch'
                    )
        
                    st.subheader("Delete a Transaction")
                    transaction_ids = [t[0] for t in transactions]
                    trans_id_to_del = st.selectbox(
                        "Select transaction to delete", 
                        options=transaction_ids, 
                        format_func=lambda x: f"ID: {x} - {next((t[2] for t in transactions if t[0] == x), 'N/A')} - ₹{next((t[4] for t in transactions if t[0] == x), 'N/A'):.2f}", 
                        key="trans_select_del")
                    st.button("Delete Selected Transaction", on_click=delete_transaction_callback, width='stretch')
        
                else:
                    st.info("No transactions found for the selected date range.")