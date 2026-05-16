name = "price"
description = "get price of crypto, gold, silver, bronze"
category = "general"

import asyncio

metalmap = {
    "gold": "XAU",
    "silver": "XAG",
    "bronze": "copper"
}

coinmap = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "ltc": "litecoin",
    "trx": "tron",
    "xrp": "ripple",
    "xmr": "monero",
    "sol": "solana"
}

async def execute(client, message):
    try:
        args = message.text.split(maxsplit=1)
        
        if len(args) < 2:
            await message.edit(await localise("usage: .price [symbol]"))
            return
        
        symbol = args[1].strip().lower()
        
        if not symbol:
            await message.edit(await localise("symbol cannot be empty"))
            return
        
        if len(symbol) > 20:
            await message.edit(await localise("symbol too long"))
            return
        
        try:
            await message.edit(await localise("fetching price..."))
        except:
            pass
        
        if symbol in metalmap:
            try:
                import aiohttp
                timeout = aiohttp.ClientTimeout(total=120)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    try:
                        if symbol == "gold":
                            url = "https://www.goldapi.io/api/XAU/USD"
                        elif symbol == "silver":
                            url = "https://www.goldapi.io/api/XAG/USD"
                        elif symbol == "bronze":
                            url = "https://api.coingecko.com/api/v3/simple/price?ids=copper&vs_currencies=usd"
                        
                        if symbol == "bronze":
                            async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                                if resp.status == 200:
                                    data = await resp.json()
                                    price = data.get("copper", {}).get("usd", 0)
                                    if price > 0:
                                        response = await localise(f"{symbol} price") + "\n\n"
                                        response += f"price: ${price:.4f} USD per lb"
                                        await message.edit(response)
                                    else:
                                        await message.edit(await localise(f"{symbol}: price unavailable"))
                                else:
                                    await message.edit(await localise(f"{symbol}: api error {resp.status}"))
                        else:
                            async with session.get(f"https://api.gold-api.com/price/{symbol}", headers={"User-Agent": "Mozilla/5.0"}) as resp:
                                if resp.status == 200:
                                    data = await resp.json()
                                    price = data.get("price")
                                    if price and price > 0:
                                        response = await localise(f"{symbol} price") + "\n\n"
                                        response += f"price: ${price:.2f} USD per oz"
                                        await message.edit(response)
                                    else:
                                        await message.edit(await localise(f"{symbol}: price unavailable"))
                                else:
                                    await message.edit(await localise(f"{symbol}: api error {resp.status}"))
                    except asyncio.TimeoutError:
                        await message.edit(await localise(f"{symbol}: request timeout"))
                    except aiohttp.ClientError as e:
                        await message.edit(await localise(f"{symbol}: network error"))
                    except ValueError:
                        await message.edit(await localise(f"{symbol}: invalid response data"))
                    except Exception as e:
                        await message.edit(await localise(f"{symbol}: fetch failed"))
            except ImportError:
                await message.edit(await localise("aiohttp not installed"))
            except Exception as e:
                await message.edit(await localise(f"error fetching metal price: {str(e)}"))
        else:
            try:
                import aiohttp
                timeout = aiohttp.ClientTimeout(total=120)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    try:
                        coinid = coinmap.get(symbol, symbol)
                        
                        async with session.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coinid}&vs_currencies=usd") as resp:
                            if resp.status == 429:
                                await message.edit(await localise(f"{symbol}: rate limited"))
                                return
                            elif resp.status == 404:
                                await message.edit(await localise(f"{symbol}: not found"))
                                return
                            elif resp.status != 200:
                                await message.edit(await localise(f"{symbol}: api error {resp.status}"))
                                return
                            
                            data = await resp.json()
                            
                            if not data or coinid not in data:
                                async with session.get(f"https://api.coingecko.com/api/v3/coins/list") as listresp:
                                    if listresp.status == 200:
                                        coins = await listresp.json()
                                        found = None
                                        for coin in coins:
                                            if coin.get("symbol", "").lower() == symbol:
                                                found = coin.get("id")
                                                break
                                        
                                        if found:
                                            async with session.get(f"https://api.coingecko.com/api/v3/simple/price?ids={found}&vs_currencies=usd") as retry:
                                                if retry.status == 200:
                                                    retrydata = await retry.json()
                                                    if found in retrydata:
                                                        data = {coinid: retrydata[found]}
                                
                                if not data or coinid not in data:
                                    await message.edit(await localise(f"{symbol}: not found or invalid symbol"))
                                    return
                            
                            price = data[coinid].get("usd", 0)
                            
                            if price <= 0:
                                await message.edit(await localise(f"{symbol}: price unavailable"))
                                return
                            
                            response = await localise(f"{symbol.upper()} price") + "\n\n"
                            response += f"price: ${price:,.8f}" if price < 1 else f"price: ${price:,.2f}"
                            
                            await message.edit(response)
                    except asyncio.TimeoutError:
                        await message.edit(await localise(f"{symbol}: request timeout"))
                    except aiohttp.ClientError:
                        await message.edit(await localise(f"{symbol}: network error"))
                    except ValueError:
                        await message.edit(await localise(f"{symbol}: invalid response data"))
                    except KeyError:
                        await message.edit(await localise(f"{symbol}: price data not found"))
                    except Exception as e:
                        await message.edit(await localise(f"{symbol}: fetch failed"))
            except ImportError:
                await message.edit(await localise("aiohttp not installed"))
            except Exception as e:
                await message.edit(await localise(f"error fetching crypto price: {str(e)}"))
    except Exception as e:
        try:
            await message.edit(await localise(f"error: {str(e)}"))
        except:
            try:
                await message.reply(await localise(f"critical error: {str(e)}"))
            except:
                pass
