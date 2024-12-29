from typing import List
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, WebSocket
from ib_insync import *
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['https://localhost:3000','https://127.0.0.1:58540','http://localhost:3000','http://80.137.37.62','https:80.137.37.62','http://80.137.37.62:59402','https:80.137.37.62:59402','https://aragon-trade.com'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Initialize Interactive Brokers connection


# Historical Candlestick Data Endpoint
@app.get("/api/stocks/{symbol}/candlesticks")
def get_historical_candlesticks(symbol: str, timeframe: str = "1 min", duration: str = "1 D"):
    """
    Fetch historical candlestick data for a given symbol and timeframe.
    """
    ib = IB()
    
    ib.connect('127.0.0.1', 7497, clientId=1)
    
    try:
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
        ib.disconnect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching historical data: {str(e)}")
        ib.disconnect()
    

# # Real-Time Candle Updates Endpoint
# @app.get("/api/stocks/{symbol}/latest-candle")
# async def get_real_time_candle(symbol: str):
#     """
#     Fetch real-time market data for the given symbol.
#     """
#     try:
#         contract = Stock(symbol, 'SMART', 'USD')
#         market_data = ib.reqMktData(contract, genericTickList='', snapshot=False)

#         def extract_realtime_data(ticker):
#             """
#             Extract and return real-time data for the ticker.
#             """
#             if ticker.last != 0:
#                 return {
#                     "time": pd.Timestamp.now().isoformat(),
#                     "last": ticker.last,
#                     "bid": ticker.bid,
#                     "ask": ticker.ask,
#                     "volume": ticker.lastSize
#                 }
#             return {}

#         # Wait briefly to receive market data
#         await asyncio.sleep(3)
#         real_time_data = extract_realtime_data(market_data)

#         if not real_time_data:
#             raise HTTPException(status_code=404, detail="No real-time data available for the given symbol.")

#         return real_time_data
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching real-time data: {str(e)}")
    
    

# Run FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="195.200.15.182", port=8000)
