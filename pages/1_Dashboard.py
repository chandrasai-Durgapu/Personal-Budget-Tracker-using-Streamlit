import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

from setup.db import (
    fetch_summary_data,
    get_total_spent_per_category,
    get_budgets_for_month
)

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access the Dashboard.")
else:
    st.header("Financial Dashboard")
    
    with st.container():
        st.subheader("Summary for Selected Period")
        
        col_date1, col_date2 = st.columns(2)
        today = datetime.date.today()
        start_date = col_date1.date_input("Start date", value=today.replace(day=1), key="dash_start_date")
        end_date = col_date2.date_input("End date", value=today, key="dash_end_date")
        
        if start_date > end_date:
            st.error("Start date must be before end date.")
        else:
            summary_data = fetch_summary_data(st.session_state.user_id, str(start_date), str(end_date + datetime.timedelta(days=1)))
            
            if not summary_data:
                st.info("No data to display for the selected date range. Try adding some transactions!")
            else:
                df_summary = pd.DataFrame(summary_data, columns=['Type', 'Total'])
                
                total_income = df_summary[df_summary['Type'] == 'income']['Total'].sum()
                total_expenses = df_summary[df_summary['Type'] == 'expense']['Total'].sum()
                total_savings = df_summary[df_summary['Type'] == 'savings']['Total'].sum()
                balance = total_income - total_expenses - total_savings
    
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Income", f"₹{total_income:,.2f}")
                col2.metric("Total Expenses", f"₹{total_expenses:,.2f}")
                col3.metric("Total Savings", f"₹{total_savings:,.2f}")
                col4.metric("Net Balance", f"₹{balance:,.2f}")
    
                chart_col1, chart_col2 = st.columns(2)
                with chart_col1:
                    st.subheader("Spending Breakdown")
                    df_spending_pie = df_summary[df_summary['Type'].isin(['expense', 'savings'])]
                    if not df_spending_pie.empty:
                        fig = px.pie(df_spending_pie, values='Total', names='Type', title='Distribution of Expenses & Savings')
                        st.plotly_chart(fig, width='stretch')
                    else:
                        st.info("No expenses or savings to show for this period.")
                
                with chart_col2:
                    st.subheader("Budget Progress")
                    
                    selected_month = end_date.month
                    selected_year = end_date.year
                    
                    budgets = get_budgets_for_month(st.session_state.user_id, selected_month, selected_year)
                    budget_dict = {b[3]: b[2] for b in budgets}
                    
                    total_spent_data = get_total_spent_per_category(st.session_state.user_id, selected_month, selected_year)
                    spent_df = pd.DataFrame(total_spent_data, columns=['ID', 'Category', 'Spent']).set_index('ID')
                    
                    chart_data = []
                    for cat_id, budget_amount in budget_dict.items():
                        spent_amount = spent_df.loc[cat_id, 'Spent'] if cat_id in spent_df.index else 0.0
                        chart_data.append({'Category': spent_df.loc[cat_id, 'Category'] if cat_id in spent_df.index else 'N/A', 
                                           'Amount': budget_amount, 'Type': 'Budget'})
                        chart_data.append({'Category': spent_df.loc[cat_id, 'Category'] if cat_id in spent_df.index else 'N/A', 
                                           'Amount': spent_amount, 'Type': 'Spent'})
                    
                    if chart_data:
                        df_chart = pd.DataFrame(chart_data)
                        fig = px.bar(
                            df_chart,
                            x='Category',
                            y='Amount',
                            color='Type',
                            barmode='group',
                            title=f'Budget vs. Spent for {datetime.date(selected_year, selected_month, 1).strftime("%B %Y")}'
                        )
                        st.plotly_chart(fig, width='stretch')
                    else:
                        st.info(f"No budgets set for {datetime.date(selected_year, selected_month, 1).strftime('%B %Y')}. Visit the Budgets page to set one!")