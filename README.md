# stock-trading-bot
Built using real-time data feed with websocket library and Alpaca API, recognises the 3 soldier candlestick pattern to buy/sell. 

## Instructions
Please ensure python is added to PATH and the following modules are installed (using pip install ...):
- websocket
- json
- requests
- dateutil.parser

The bot utilises an API from Alpaca, which requires registration. Upon registering an API key and secret API key must be generated and copied into the bot script.  

Feel free to pull this repo and navigate to the local directory, then enter the command ```python bot2.py``` to run the application. Results of any buying/selling will show on the Alpaca developer dashboard.

