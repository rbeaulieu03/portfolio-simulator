# %% Import necessary libraries
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt

# --- STREAMLIT UI SETUP ---
st.title("📈 Dollar-Cost Averaging (DCA) vs Lump-Sum Investment Simulator")

# Sidebar inputs
with st.sidebar.form("input_form"):
    st.header("Simulation Settings")

    ticker = st.text_input("Enter the asset ticker (e.g., SPY, AAPL, BTC-USD):", value="SPY").strip().upper()
    investment_amount = st.number_input("Investment amount per period ($):", value=200.0, step=10.0)
    lump_sum_amount = st.number_input("Total Lump-Sum investment amount ($):", value=10000.0, step=100.0)
    start_date = st.date_input("Start date:", value=datetime(2020, 1, 1))

    use_today = st.checkbox("Use today's date as the end date?", value=True)
    if use_today:
        end_date = datetime.today()
    else:
        end_date = st.date_input("Custom end date:", value=datetime.today())

    st.write("Valid investment frequencies: daily, weekly, monthly, quarterly, semiannually, annually")
    frequency = st.selectbox("Select investment frequency:",
                             options=["daily", "weekly", "monthly", "quarterly", "semiannually", "annually"],
                             index=2)

    submitted = st.form_submit_button("Run Simulation")

# --- MAIN LOGIC ---
if submitted:

    # Normalize start and end dates
    start_date_obj = datetime.combine(start_date, datetime.min.time())
    end_date_obj = datetime.combine(end_date, datetime.min.time())
    start_date_str = start_date_obj.strftime('%Y-%m-%d')
    end_date_str = end_date_obj.strftime('%Y-%m-%d')

    # STEP 3: Download price data from yfinance
    data = yf.download(ticker, start=start_date_str, end=end_date_str)

    if data.empty:
        st.error(f"No data was retrieved for ticker '{ticker}'. Check the ticker and date range.")
        st.stop()

    # Reset index to access 'Date' column
    data.reset_index(inplace=True)

    # Flatten column headers if they're MultiIndex
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [' '.join(col).strip() for col in data.columns]

    # Try multiple versions of price columns (with and without ticker suffix)
    possible_cols = [
        'Adj Close', f'Adj Close {ticker}',
        'Close', f'Close {ticker}'
    ]
    price_column = next((col for col in possible_cols if col in data.columns), None)

    if not price_column:
        st.error(f"No usable price column found. Columns: {list(data.columns)}")
        st.stop()
    elif 'Adj Close' not in price_column:
        st.warning("⚠️ 'Adj Close' not available — using 'Close' instead.")

    # Reduce dataset to just Date and the selected price column
    data = data[['Date', price_column]]
    data['Date'] = pd.to_datetime(data['Date'])

    # STEP 4: Generate investment schedule
    def generate_schedule(start_date, end_date, frequency, trading_days):
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        schedule = []
        current = start

        while current <= end:
            raw_date = current.strftime('%Y-%m-%d')
            while raw_date not in trading_days:
                current += timedelta(days=1)
                raw_date = current.strftime('%Y-%m-%d')

            schedule.append(raw_date)

            if frequency == 'daily':
                current += timedelta(days=1)
            elif frequency == 'weekly':
                current += timedelta(weeks=1)
            elif frequency == 'monthly':
                current = current.replace(day=1) + pd.DateOffset(months=1)
                current = current.replace(day=start.day if start.day <= 28 else 28)
            elif frequency == 'quarterly':
                current = current.replace(day=1) + pd.DateOffset(months=3)
                current = current.replace(day=start.day if start.day <= 28 else 28)
            elif frequency == 'semiannually':
                current = current.replace(day=1) + pd.DateOffset(months=6)
                current = current.replace(day=start.day if start.day <= 28 else 28)
            elif frequency == 'annually':
                current = current.replace(day=1) + pd.DateOffset(years=1)
                current = current.replace(day=start.day if start.day <= 28 else 28)
            else:
                raise ValueError("Invalid frequency.")

        return schedule

    # Get valid trading days from dataset
    trading_days = sorted(data['Date'].dt.strftime('%Y-%m-%d').tolist())

    # Generate investment dates
    schedule = generate_schedule(start_date_str, end_date_str, frequency, trading_days)

    # STEP 5: Run DCA simulation
    total_contributions = 0
    total_shares = 0

    for date in schedule:
        price = data[data['Date'] == pd.to_datetime(date)][price_column].values[0]
        shares_bought = investment_amount / price
        total_contributions += investment_amount
        total_shares += shares_bought

    # STEP 6: Final performance results
    latest_price = data[price_column].iloc[-1]
    ending_value_dca = total_shares * latest_price
    growth_dca = ending_value_dca - total_contributions
    return_pct_dca = (growth_dca / total_contributions) * 100

    # STEP 6.5: Calculate CAGR
    years = (end_date_obj - start_date_obj).days / 365.25
    if years > 0 and total_contributions > 0:
        cagr_dca = ((ending_value_dca / total_contributions) ** (1 / years)) - 1
    else:
        cagr_dca = 0.0

    # --- Now Calculate Lump Sum ---
    monthly_data = data.set_index('Date').resample('M').last()
    initial_price = monthly_data[price_column].iloc[0]
    shares_lump_sum = lump_sum_amount / initial_price
    portfolio_value_lump_sum = shares_lump_sum * monthly_data[price_column]

    # --- Calculate DCA Portfolio Value Over Time ---
    shares_dca = (investment_amount / monthly_data[price_column]).fillna(0)
    cumulative_shares_dca = shares_dca.cumsum()
    portfolio_value_dca_over_time = cumulative_shares_dca * monthly_data[price_column]

    # --- Plot the results ---
    st.subheader("📊 Portfolio Growth Over Time")

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(portfolio_value_dca_over_time.index, portfolio_value_dca_over_time.values, label='Dollar-Cost Averaging (DCA)', linewidth=2)
    ax.plot(portfolio_value_lump_sum.index, portfolio_value_lump_sum.values, label='Lump-Sum Investment', linewidth=2, linestyle='--')
    ax.set_title(f"Portfolio Growth Simulation: {ticker}", fontsize=16)
    ax.set_xlabel("Date", fontsize=14)
    ax.set_ylabel("Portfolio Value ($)", fontsize=14)
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # STEP 7: Output results
    st.subheader("===== Investment Simulation Results =====")
    st.text(f"Asset Ticker: {ticker}")
    st.text(f"Investment Start Date: {start_date_str}")
    st.text(f"Investment End Date: {end_date_str}")
    st.text(f"Investment Frequency: {frequency.capitalize()}")
    st.text(f"--- DCA ---")
    st.text(f"Total Contributions: ${total_contributions:,.2f}")
    st.text(f"Total Shares Accumulated: {total_shares:,.4f}")
    st.text(f"Final Portfolio Value (DCA): ${ending_value_dca:,.2f}")
    st.text(f"Total Growth (DCA): ${growth_dca:,.2f}")
    st.text(f"Total Return (DCA): {return_pct_dca:.2f}%")
    st.text(f"Average Annual Return (CAGR - DCA): {cagr_dca * 100:.2f}%")
    st.text(f"--- Lump Sum ---")
    st.text(f"Total Initial Investment: ${lump_sum_amount:,.2f}")
    st.text(f"Final Portfolio Value (Lump Sum): ${portfolio_value_lump_sum.iloc[-1]:,.2f}")
    st.text(f"Total Return (Lump Sum): {((portfolio_value_lump_sum.iloc[-1] - lump_sum_amount) / lump_sum_amount) * 100:.2f}%")
# %%
