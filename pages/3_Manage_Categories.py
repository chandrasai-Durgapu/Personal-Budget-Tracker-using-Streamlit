import streamlit as st
import pandas as pd
import io

from setup.db import (
    get_user_categories,
    add_category,
    update_category,
    delete_category
)

# --- Callbacks for database operations ---
def add_category_callback():
    st.session_state.add_submitted = True

def update_categories_callback():
    st.session_state.update_submitted = True

def delete_category_callback():
    st.session_state.delete_submitted = True
    
# --- Initialize session state for all forms and actions ---
if 'add_submitted' not in st.session_state:
    st.session_state.add_submitted = False
if 'update_submitted' not in st.session_state:
    st.session_state.update_submitted = False
if 'delete_submitted' not in st.session_state:
    st.session_state.delete_submitted = False

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to manage your Categories.")
else:
    st.header("Manage Categories")

    # --- Add New Category Form ---
    with st.container():
        st.subheader("Add New Category")
        with st.form('category_form', clear_on_submit=True):
            category_name = st.text_input('Category Name')
            category_type = st.selectbox('Category Type', ['expense', 'income', 'savings'])
            
            st.form_submit_button('Add Category', on_click=add_category_callback)

        if st.session_state.add_submitted:
            st.session_state.add_submitted = False
            if not category_name.strip():
                st.error("Category name cannot be empty.")
            else:
                add_category(st.session_state.user_id, category_name.strip(), category_type)
                st.success("Category added successfully!")
                

    # --- Fetch categories for display ---
    categories = get_user_categories(st.session_state.user_id)
    df_categories = pd.DataFrame(categories, columns=['ID', 'Category Name', 'Category Type'])

    # --- Editable Category Table ---
    with st.container():
        st.subheader("Your Categories")
        if not categories:
            st.info("You have no categories yet. Add one above.")
        else:
            editable_df = st.data_editor(
                df_categories,
                hide_index=True,
                width='stretch',
                key="category_editor",
                column_config={
                    "ID": None,
                    "Category Name": st.column_config.TextColumn("Category Name", required=True),
                    "Category Type": st.column_config.SelectboxColumn("Category Type", options=['expense', 'income', 'savings'], required=True)
                }
            )

            st.info("Edit a row in the table above and click 'Save Changes' to update it.")
            
            st.button("Save Changes to Categories", on_click=update_categories_callback, width='stretch')

        if st.session_state.update_submitted:
            st.session_state.update_submitted = False
            for _, row in editable_df.iterrows():
                try:
                    update_category(row['ID'], row['Category Name'], row['Category Type'])
                except Exception as e:
                    st.error(f"Failed to update category {row['ID']}: {e}")
            
            st.success("Categories updated successfully!")
            

    # --- Delete a Category Section ---
    with st.container():
        st.subheader("Delete a Category")
        if categories:
            category_options = {c[1]: c[0] for c in categories}
            selected_category_name = st.selectbox(
                "Select a category to delete",
                options=list(category_options.keys()),
                key="category_select_del"
            )
            st.button("Delete Selected Category", on_click=delete_category_callback, width='stretch')
        else:
            st.info("No categories to delete.")

    if st.session_state.delete_submitted:
        st.session_state.delete_submitted = False
        cat_id_to_del = category_options.get(st.session_state.category_select_del)
        if cat_id_to_del:
            delete_category(cat_id_to_del)
            st.success("Category and all related transactions deleted.")
        else:
            st.error("Please select a category to delete.")

    # Download Button
    df_categories = pd.DataFrame(get_user_categories(st.session_state.user_id), columns=['ID', 'Category Name', 'Category Type'])
    st.download_button(
        label="Download Categories as CSV",
        data=io.StringIO(df_categories.to_csv(index=False)).getvalue(),
        file_name=f"categories_{st.session_state.username}.csv",
        mime="text/csv",
        width='stretch'
    )