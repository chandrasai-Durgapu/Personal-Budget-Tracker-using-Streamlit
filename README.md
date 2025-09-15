# 💰 Personal Budget Tracker

[![Streamlit App](https://img.shields.io/badge/Streamlit-Live-green?logo=streamlit)](https://personal-budget-tracker.streamlit.app/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)



**Track your spending, manage your finances, and achieve your financial goals with ease.**

This is a personal budget management application built with Streamlit and SQLite. It offers a simple yet powerful interface to log income and expenses, set monthly budgets, and visualize your financial health through interactive charts.

---

## 🌐 Live Demo

👉 **Try it now:** [https://personal-budget-tracker.streamlit.app/](https://personal-budget-tracker.streamlit.app/)

---

## 🖼️ Screenshot

![App Screenshot](https://github.com/<your-username>/<your-repo>/raw/main/assets/screenshot.png)

---

## ✨ Features

## 🔐 User Authentication:
 Secure login system with unique User ID and password.

## 📊 Intuitive Dashboard:
 Overview of income, expenses, and net balance for any selected period.

## 🏷️ Dynamic Categories:
 Create, edit, and delete custom categories (e.g., Groceries, Rent, Salary).

## 💼 Transaction Management:
 Add, edit, and delete transactions with details like date, amount, category, and notes.

## 📆 Interactive Budgets: 
Set monthly budgets and compare actual spending with "Budget vs. Actual" charts.

## 📈 Financial Insights: 
Visualize spending patterns and balance trends over time using Plotly.

## 📤 Data Export: 
Download transaction and category data as CSV files.

## 🧑‍💻 Modern UI: 
Clean, responsive, and user-friendly interface powered by Streamlit.

---

## 🚀 Getting Started
### ✅ Prerequisites

Python 3.10 or higher

conda (recommended) or pip for managing environments

---

## 🛠️ Installation Steps
1. Clone the Repository

```bash
git clone https://github.com/chandrasai-Durgapu/Personal-Budget-Tracker-using-Streamlit.git

```

```bash
# change directory
cd Personal-Budget-Tracker-using-Streamlit
```

2. Create and Activate Virtual Environment

Using Conda (recommended):
```bash
# Create Conda environment
conda create -n budgettracker python=3.10 -y
# Activate Conda environment
conda activate budgettracker
```

Or using venv:

```bash
python -m venv budgettracker
```

# On Windows
```bash
budgettracker\Scripts\activate
```

# On macOS/Linux
```bash
source budgettracker/bin/activate
```

3. Install Dependencies
```bash
pip install -r requirements.txt
```

4. Run the Application
```bash
streamlit run app.py
```


The application will launch in your browser at http://localhost:8501
.
---

### 📂 Project Structure

.
├── .streamlit/             # Streamlit configuration for theming
├── pages/                  # Main application pages
│   ├── 1_Dashboard.py
│   ├── 2_Transactions.py
│   ├── 3_Manage_Categories.py
│   ├── 4_Budgets.py
│   └── 5_Insights.py
├── setup/                  # Backend and database logic
│   └── db.py
├── app.py                  # Main entry point
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
└── budget_tracker.db       # SQLite database (auto-generated on first run)


---

## 🤝 Contributing

Contributions are welcome and appreciated!

Fork the repository

Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```


Commit your changes:
```bash
git commit -am 'feat: Add new feature'
```

Push the branch:
```bash
git push origin feature/your-feature-name
```

Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License