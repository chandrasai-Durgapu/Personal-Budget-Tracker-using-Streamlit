import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

from setup.db import fetch_transaction_history

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to view your Financial Insights.")
else:
    st.header("Financial Insights")
    st.info("This page provides a high-level overview of your spending habits over time.")

    transactions = fetch_transaction_history(st.session_state.user_id)
    if not transactions:
        st.warning("No transactions found. Add some to see your insights!")
    else:
        df = pd.DataFrame(transactions, columns=['ID', 'Date', 'Category', 'Type', 'Amount', 'Note'])
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')
    
        # Calculate daily net balance
        df_net = df.copy()
        df_net['Amount'] = df_net.apply(lambda row: -row['Amount'] if row['Type'] == 'expense' else row['Amount'], axis=1)
        df_daily = df_net.groupby('Date')['Amount'].sum().reset_index()
        df_daily['Balance'] = df_daily['Amount'].cumsum()
    
        st.subheader("Net Balance Over Time")
        if not df_daily.empty:
            fig = px.line(df_daily, x='Date', y='Balance', title='Daily Balance Over Time', markers=True)
            fig.update_layout(xaxis_title="Date", yaxis_title="Balance (₹)", hovermode="x unified")
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("Not enough data to create a balance chart.")
    
        # --- Spending by Category over time (New Feature) ---
        st.subheader("Spending by Category")
        df_expenses = df[df['Type'] == 'expense'].copy()
    
        if not df_expenses.empty:
            fig = px.bar(
                df_expenses,
                x='Date',
                y='Amount',
                color='Category',
                title='Spending by Category Over Time',
                labels={'Amount': 'Amount (₹)', 'Date': 'Date'},
                hover_data={'Amount': ':.2f', 'Category': True, 'Date': False}
            )
            fig.update_layout(barmode='stack', xaxis_title="Date", yaxis_title="Amount (₹)")
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No expenses found to display.")