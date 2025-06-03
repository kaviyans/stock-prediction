from flask import Flask, request, jsonify
from flask_cors import CORS # Import CORS
import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import logging

# Configure logging for better error visibility
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
CORS(app) # Enable CORS for all routes

def get_stock_data(ticker):
    try:
        # Download 1 year of daily data, auto-adjusting for splits/dividends
        data = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)
        # Reset index to make 'Date' a regular column
        data = data.reset_index()
        return data
    except Exception as e:
        logging.error(f"Error downloading data for {ticker}: {e}")
        return pd.DataFrame() # Return an empty DataFrame on error

def predict_next_day_close(data):
    data['Day'] = np.arange(len(data))
    # Features (independent variable) - the day number
    X = data[['Day']]
    # Target (dependent variable) - the closing price
    y = data['Close']

    # Initialize and train the Linear Regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predict for the next day (length of data represents the next day's index)
    next_day_index = np.array([[len(data)]])
    pred = model.predict(next_day_index)

    # Return the predicted value as a float
    return float(pred.item())


@app.route('/predict', methods=['GET'])
def predict():
    ticker = request.args.get('ticker', default='AAPL').upper() # Convert to uppercase for consistency
    try:
        data = get_stock_data(ticker)

        # Check if data was successfully retrieved
        if data.empty:
            return jsonify({'error': f'No data found for ticker {ticker}. Please check the ticker symbol.'}), 400

        # Get the latest closing price
        # Using .item() to robustly extract the scalar value from the Series,
        # which resolves the FutureWarning.
        latest_close = (data['Close'].iloc[-1].item())*85

        # Get the predicted next day's closing price using the dedicated function
        prediction = (predict_next_day_close(data)) * 85

        # Prepare last 30 days data for charting
        last_30 = data.tail(30)

        # Convert dates to string format and then to a Python list
        dates = pd.to_datetime(last_30['Date']).dt.strftime('%Y-%m-%d').tolist()

        # Convert closes to a Python list, ensuring robustness for the reported error
        # .values converts the Series to a NumPy array, then .tolist() converts the array to a list
        closes = last_30['Close'].round(2).values.tolist()

        # Return the results as a JSON response
        return jsonify({
            'ticker': ticker,
            # Format latest_close and predicted_close with Rupee symbol
            'latest_close': f'₹{round(latest_close, 2)}',
            'predicted_close': f'₹{round(prediction, 2)}',
            'dates': dates,
            'closes': closes
        })

    except Exception as e:
        logging.exception(f"Error processing prediction for ticker {ticker}")
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)