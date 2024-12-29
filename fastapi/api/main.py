from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from ib_insync import *
import uvicorn
import threading

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'https://localhost:3000',
        'http://localhost:3000',
        'http://80.137.37.62',
        'https://aragon-trade.com',
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Global IB instance
ib = IB()

# Mutex for thread safety
ib_lock = threading.Lock()

def connect_to_ib():
    """
    Connect to Interactive Brokers in a separate thread.
    """
    with ib_lock:
        try:
            if not ib.isConnected():
                ib.connect('127.0.0.1', 7497, clientId=1)
                print("Connected to Interactive Brokers")
        except Exception as e:
            print(f"Error connecting to Interactive Brokers: {e}")

def disconnect_from_ib():
    """
    Disconnect from Interactive Brokers in a separate thread.
    """
    with ib_lock:
        if ib.isConnected():
            ib.disconnect()
            print("Disconnected from Interactive Brokers")

@app.on_event("startup")
def on_startup():
    """
    Connect to Interactive Brokers when the app starts.
    """
    connect_to_ib()

@app.on_event("shutdown")
def on_shutdown():
    """
    Disconnect from Interactive Brokers when the app shuts down.
    """
    disconnect_from_ib()

@app.get("/api/stocks/{symbol}/candlesticks")
def get_historical_candlesticks(symbol: str, timeframe: str = "1 min", duration: str = "1 D"):
    """
    Fetch historical candlestick data for a given symbol and timeframe.
    """
    try:
        with ib_lock:
            # Ensure connection
            connect_to_ib()

            # Define stock contract
            contract = Stock(symbol, 'SMART', 'USD')

            # Request historical data
            bars = ib.reqHistoricalData(
                contract,
                endDateTime='',
                durationStr=duration,
                barSizeSetting=timeframe,
                whatToShow='TRADES',
                useRTH=True,
            )

            if not bars:
                raise HTTPException(status_code=404, detail="No historical data found for the given symbol.")

            # Convert data to JSON format
            data = [
                {
                    "time": bar.date.isoformat(),
                    "open": bar.open,
                    "high": bar.high,
                    "low": bar.low,
                    "close": bar.close,
                    "volume": bar.volume,
                }
                for bar in bars
            ]
            return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching historical data: {str(e)}")

# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
