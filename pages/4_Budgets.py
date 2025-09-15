import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

from setup.db import (
    get_user_categories,
    set_budget,
    get_budgets_for_month,
    get_total_spent_per_category
)

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to manage your Budgets.")
else:
    st.header("Monthly Budgets")
    categories = get_user_categories(st.session_state.user_id)
    if not categories:
        st.warning("Please add some categories first.")
    else:
        categories_df = pd.DataFrame(categories, columns=['ID', 'Category Name', 'Category Type'])
        expense_categories = categories_df[categories_df['Category Type'] == 'expense']
    
        if expense_categories.empty:
            st.info("You don't have any expense categories yet. Budgets can only be set for expenses.")
        else:
            col1, col2 = st.columns(2)
            selected_month = col1.selectbox('Month', list(range(1, 13)), index=datetime.date.today().month - 1)
            selected_year = col2.number_input('Year', min_value=2000, max_value=2100, value=datetime.date.today().year, step=1)
    
            budgets = get_budgets_for_month(st.session_state.user_id, selected_month, selected_year)
            budget_dict = {b[3]: b[2] for b in budgets}
    
            with st.container():
                st.subheader("Set Budgets")
                with st.form('budget_form'):
                    st.write(f"**Set Budgets for {datetime.date(selected_year, selected_month, 1).strftime('%B %Y')}**")
                    budget_inputs = {}
                    for _, row in expense_categories.iterrows():
                        cat_id = row['ID']
                        cat_name = row['Category Name']
                        
                        budget_inputs[cat_id] = st.number_input(
                            f"Budget for {cat_name}",
                            min_value=0.0,
                            value=float(budget_dict.get(cat_id, 0.0)),
                            key=f"budget_input_{cat_id}"
                        )
                    
                    submitted = st.form_submit_button('Save Budgets')
                    if submitted:
                        for cat_id, amount in budget_inputs.items():
                            set_budget(st.session_state.user_id, cat_id, selected_month, selected_year, amount)
                        st.success("Budgets saved successfully!")
            
            with st.container():
                st.subheader("Budget vs. Actual Spending")
                total_spent_data = get_total_spent_per_category(st.session_state.user_id, selected_month, selected_year)
                spent_df = pd.DataFrame(total_spent_data, columns=['ID', 'Category', 'Spent']).set_index('ID')
                
                chart_data = []
                for _, row in expense_categories.iterrows():
                    cat_id = row['ID']
                    cat_name = row['Category Name']
                    budget_amount = budget_dict.get(cat_id, 0.0)
                    spent_amount = spent_df.loc[cat_id, 'Spent'] if cat_id in spent_df.index else 0.0
                    
                    chart_data.append({'Category': cat_name, 'Amount': budget_amount, 'Type': 'Budget'})
                    chart_data.append({'Category': cat_name, 'Amount': spent_amount, 'Type': 'Spent'})
        
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
                    st.info("No budgets to display. Set some budgets in the section above!")