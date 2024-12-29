from ib_insync import IB
from fastapi import FastAPI, HTTPException, WebSocket

app = FastAPI()

@app.get("/api/stocks/{symbol}/candlesticks")
def get_historical_candlesticks(symbol: str, timeframe: str = "1 min", duration: str = "1 D"):
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)
    print("Connected:", ib.isConnected())
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
#         raise HTTPException(status_code=500, detail=f"Error fetching real-time data: {str(e)}"
