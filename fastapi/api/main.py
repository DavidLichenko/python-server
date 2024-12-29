from ib_insync import *
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from concurrent.futures import ThreadPoolExecutor
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get("/api/stocks/{symbol}/candlesticks/")
def get_historical_candlesticks(symbol: str, timeframe: str = "1 min", duration: str = "1 D"):
    # Create a new event loop for the thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)  # Set the new event loop as the current loop

    ib = IB()
    loop.run_until_complete(ib.connectAsync('127.0.0.1', 7497, clientId=random.randint(1, 1000)))
    contract = Stock(symbol, 'SMART', 'USD')
    bars = ib.reqHistoricalData(
        contract,
        endDateTime='',
        durationStr=duration,
        barSizeSetting=timeframe,
        whatToShow='TRADES',
        useRTH=True
    )

    if not bars:
        raise HTTPException(status_code=404, detail="No historical data found for the given symbol.")

        # Convert data to JSON format for frontend
    data = [
        {
            "time": bar.date.isoformat(),
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": bar.volume
        }
        for bar in bars
    ]
    ib.disconnect()
    return data
    # Perform your tasks (e.g., requesting historical data)
