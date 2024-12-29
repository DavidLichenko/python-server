from ib_insync import *
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from concurrent.futures import ThreadPoolExecutor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['https://localhost:3000','https://127.0.0.1:58540','http://localhost:3000','http://80.137.37.62','https:80.137.37.62','http://80.137.37.62:59402','https:80.137.37.62:59402','https://aragon-trade.com'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get("/api/stocks/{symbol}/candlesticks/")
async def get_historical_candlesticks(symbol: str, timeframe: str = "1 min", duration: str = "1 D"):
    ib = IB()
    try:
        # Ensure no previous connection exists
        if ib.isConnected():
            ib.disconnect()

        # Connect to IB with a unique clientId and increased timeout
        await ib.connectAsync('127.0.0.1', 7497, clientId=1, timeout=30)
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
        return data
    finally:
        # Ensure that the IB client is disconnected
        ib.disconnect()
