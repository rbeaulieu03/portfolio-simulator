# portfolio-simulator
Project Overview
The Portfolio Simulator is an educational and analytical tool that helps users visualize the impact of compounding returns and dollar-cost averaging (DCA) strategies over time. By simulating investments using historical stock data, users can explore how different approaches to investing could have influenced portfolio growth.

Team Members:
Aaron Garcia
Raymond Beaulieu
Luke Crumpler
Matthew Skinner

Features
Simulate historical investments based on a stock ticker.

Compare Lump-Sum vs Dollar-Cost Averaging (DCA) strategies.

Visualize portfolio growth with interactive graphs.

Display final portfolio values, returns, and basic risk metrics.

Technologies
Python

Pandas, NumPy: Data handling and analysis

yfinance: Fetch historical stock prices

Matplotlib, Plotly: Data visualization

Streamlit (or Dash): Web application framework

SQLite or CSV: Store user input history

Scipy, Statsmodels: Statistical analysis

Project Structure
bash
Copy
Edit
/portfolio-simulator/
│
├── app.py             # Main Streamlit/Dash application
├── requirements.txt   # List of required Python libraries
├── README.md          # Project documentation (this file)
├── data/              # (Optional) Folder for any local datasets
├── assets/            # (Optional) Images or CSS for UI
└── utils.py           # Helper functions for backend logic
How to Run
Clone the repository:

bash
Copy
Edit
git clone https://github.com/your-username/portfolio-simulator.git
cd portfolio-simulator
Set up a virtual environment (recommended):

bash
Copy
Edit
python -m venv venv
source venv/bin/activate        # macOS/Linux
.\venv\Scripts\activate          # Windows
Install the required packages:

nginx
Copy
Edit
pip install -r requirements.txt
Run the app:

arduino
Copy
Edit
streamlit run app.py
or, if using Dash:

nginx
Copy
Edit
python app.py
Learning Goals
Deepen understanding of compounding and DCA in investing.

Practice Python programming for financial analytics.

Build web applications and visualize financial data interactively.

Future Extensions
Allow simulation of multiple assets for portfolio diversification.

Add Monte Carlo simulations for forecasting.

Integrate real-time brokerage APIs for live investing simulations.

