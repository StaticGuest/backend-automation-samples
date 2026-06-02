import asyncio
import logging
import os
import sys
from typing import Dict, List, Optional
import aiohttp

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("DataPipeline")

CONFIG = {
    "BASE_URL": "https://api.binance.com/api/v3/ticker/price",
    "TARGET_SYMBOLS": ["BTCUSDT", "ETHUSDT", "SOLUSDT", "LINKUSDT"],
    "REQUEST_TIMEOUT": 10,  # таймаут відповіді в секундах
    "MAX_RETRIES": 3,       # кількість спроб при збої мережі
    "RETRY_DELAY": 2,       # затримка між спробами у секундах
}

async def fetch_symbol_price(session: aiohttp.ClientSession, symbol: str) -> Optional[Dict[str, str]]:
    url = CONFIG["BASE_URL"]
    params = {"symbol": symbol}

    for attempt in range(1, CONFIG["MAX_RETRIES"] + 1):
        try:
            async with session.get(url, params=params, timeout=CONFIG["REQUEST_TIMEOUT"]) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "symbol": data.get("symbol"),
                        "price": data.get("price")
                    }
                elif response.status == 429:
                    logger.warning(f"Rate limit hit for {symbol}. Attempt {attempt}/{CONFIG['MAX_RETRIES']}.")
                else:
                    logger.error(f"API returned status {response.status} for {symbol}. Attempt {attempt}/{CONFIG['MAX_RETRIES']}.")
        
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Connection error for {symbol}: {str(e)}. Attempt {attempt}/{CONFIG['MAX_RETRIES']}.")
        except asyncio.TimeoutError:
            logger.error(f"Timeout reached for {symbol}. Attempt {attempt}/{CONFIG['MAX_RETRIES']}.")
        except Exception as e:
            logger.error(f"Unexpected error fetching {symbol}: {str(e)}. Attempt {attempt}/{CONFIG['MAX_RETRIES']}.")

        if attempt < CONFIG["MAX_RETRIES"]:
            await asyncio.sleep(CONFIG["RETRY_DELAY"])

    return None

async def main():
    logger.info("Initializing asynchronous data extraction pipeline...")
    logger.info("Configuration successfully verified.")

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_symbol_price(session, symbol) for symbol in CONFIG["TARGET_SYMBOLS"]]
        
        logger.info(f"Dispatched {len(tasks)} concurrent API tasks. Executing...")
        results = await asyncio.gather(*tasks)

        cleaned_data = [res for res in results if res is not None]

        logger.info("=== Processed Data Pipeline Results ===")
        for record in cleaned_data:
            logger.info(f"Asset: {record['symbol']:<10} | Current Market Price: {record['price']}")
        
        logger.info(f"Pipeline finished. Successfully processed {len(cleaned_data)}/{len(CONFIG['TARGET_SYMBOLS'])} metrics.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Pipeline execution gracefully stopped by user via KeyboardInterrupt.")
    except Exception as e:
        logger.critical(f"Pipeline crashed due to an unhandled exception: {str(e)}")
