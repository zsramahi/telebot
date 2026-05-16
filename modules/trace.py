name = "trace"
aliases = ["check"]
description = "trace crypto address or transaction"
category = "crypto"

import re
import asyncio
from datetime import datetime

def detect(input):
    input = input.strip()
    if re.match(r"^0x[a-fA-F0-9]{40}$", input):
        return "eth_address"
    elif re.match(r"^0x[a-fA-F0-9]{64}$", input):
        return "eth_tx"
    elif re.match(r"^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$", input) or re.match(r"^bc1[a-z0-9]{39,59}$", input):
        return "btc_address"
    elif re.match(r"^[LM][a-km-zA-HJ-NP-Z1-9]{26,33}$", input) or re.match(r"^ltc1[a-z0-9]{39,59}$", input):
        return "ltc_address"
    elif re.match(r"^T[a-zA-Z0-9]{33}$", input):
        return "trx_address"
    elif re.match(r"^r[a-zA-Z0-9]{24,34}$", input):
        return "xrp_address"
    elif re.match(r"^[a-fA-F0-9]{64}$", input):
        return "generic_tx"
    elif len(input) >= 87 and len(input) <= 88:
        return "sol_tx"
    elif len(input) == 44 or len(input) == 43:
        try:
            import base58
            decoded = base58.b58decode(input)
            if len(decoded) == 32:
                return "sol_address"
        except:
            pass
    elif len(input) == 95:
        return "xmr_address"
    return "unknown"

async def getprice(symbol, session):
    try:
        async with session.get(f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd") as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get(symbol, {}).get("usd", 0)
    except:
        pass
    return 0

async def fetcheth(address, session):
    try:
        balance = 0
        txs = []
        
        async with session.get(f"https://blockscout.com/eth/mainnet/api?module=account&action=balance&address={address}", headers={"User-Agent": "Mozilla/5.0"}) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data.get("status") == "1":
                    balance = int(data["result"]) / 1e18
        
        async with session.get(f"https://blockscout.com/eth/mainnet/api?module=account&action=txlist&address={address}&page=1&offset=5&sort=desc", headers={"User-Agent": "Mozilla/5.0"}) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data.get("status") == "1" and data.get("result"):
                    txs = data.get("result", [])[:5]
        
        price = await getprice("ethereum", session)
        return balance, txs, price, f"https://etherscan.io/address/{address}"
    except Exception as e:
        return None, [], 0, f"https://etherscan.io/address/{address}"

async def fetchethtx(txhash, session):
    try:
        tx = None
        async with session.get(f"https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash={txhash}") as resp:
            if resp.status == 200:
                data = await resp.json()
                tx = data.get("result")
        
        receipt = None
        async with session.get(f"https://api.etherscan.io/api?module=proxy&action=eth_getTransactionReceipt&txhash={txhash}") as resp:
            if resp.status == 200:
                data = await resp.json()
                receipt = data.get("result")
        
        price = await getprice("ethereum", session)
        return tx, receipt, price, f"https://etherscan.io/tx/{txhash}"
    except:
        return None, None, 0, f"https://etherscan.io/tx/{txhash}"

async def fetchbtc(address, session):
    try:
        balance = 0
        txs = []
        async with session.get(f"https://blockchain.info/rawaddr/{address}?limit=5") as resp:
            if resp.status == 200:
                data = await resp.json()
                balance = data.get("final_balance", 0) / 1e8
                txs = data.get("txs", [])[:5]
        
        price = await getprice("bitcoin", session)
        return balance, txs, price, f"https://blockchain.info/address/{address}"
    except:
        return None, [], 0, f"https://blockchain.info/address/{address}"

async def fetchbtctx(txhash, session):
    try:
        tx = None
        async with session.get(f"https://blockchain.info/rawtx/{txhash}") as resp:
            if resp.status == 200:
                tx = await resp.json()
        
        price = await getprice("bitcoin", session)
        return tx, price, f"https://blockchain.info/tx/{txhash}"
    except:
        return None, 0, f"https://blockchain.info/tx/{txhash}"

async def fetchltc(address, session):
    try:
        balance = 0
        txs = []
        
        async with session.get(f"https://litecoinspace.org/api/address/{address}", headers={"User-Agent": "Mozilla/5.0"}) as resp:
            if resp.status == 200:
                data = await resp.json()
                funded = data.get("chain_stats", {}).get("funded_txo_sum", 0)
                spent = data.get("chain_stats", {}).get("spent_txo_sum", 0)
                balance = (funded - spent) / 1e8
                
                txlist = data.get("chain_stats", {}).get("tx_count", 0)
                if txlist > 0:
                    async with session.get(f"https://litecoinspace.org/api/address/{address}/txs", headers={"User-Agent": "Mozilla/5.0"}) as txresp:
                        if txresp.status == 200:
                            txdata = await txresp.json()
                            for tx in txdata[:5]:
                                txs.append(tx)
        
        price = await getprice("litecoin", session)
        return balance, txs, price, f"https://blockchair.com/litecoin/address/{address}"
    except Exception as e:
        return None, [], 0, f"https://blockchair.com/litecoin/address/{address}"

async def fetchltctx(txhash, session):
    try:
        tx = None
        async with session.get(f"https://litecoinspace.org/api/tx/{txhash}", headers={"User-Agent": "Mozilla/5.0"}) as resp:
            if resp.status == 200:
                tx = await resp.json()
        
        price = await getprice("litecoin", session)
        return tx, price, f"https://litecoinspace.org/tx/{txhash}"
    except:
        return None, 0, f"https://litecoinspace.org/tx/{txhash}"

async def fetchtrx(address, session):
    try:
        balance = 0
        async with session.get(f"https://apilist.tronscanapi.com/api/account?address={address}") as resp:
            if resp.status == 200:
                data = await resp.json()
                balance = data.get("balance", 0) / 1e6
        
        txs = []
        async with session.get(f"https://apilist.tronscanapi.com/api/transaction?sort=-timestamp&count=true&limit=5&start=0&address={address}") as resp:
            if resp.status == 200:
                data = await resp.json()
                txs = data.get("data", [])[:5]
        
        price = await getprice("tron", session)
        return balance, txs, price, f"https://tronscan.org/#/address/{address}"
    except:
        return None, [], 0, f"https://tronscan.org/#/address/{address}"

async def fetchtrxtx(txhash, session):
    try:
        tx = None
        async with session.get(f"https://apilist.tronscanapi.com/api/transaction-info?hash={txhash}") as resp:
            if resp.status == 200:
                tx = await resp.json()
        
        price = await getprice("tron", session)
        return tx, price, f"https://tronscan.org/#/transaction/{txhash}"
    except:
        return None, 0, f"https://tronscan.org/#/transaction/{txhash}"

async def fetchxrp(address, session):
    try:
        balance = 0
        async with session.get(f"https://api.xrpscan.com/api/v1/account/{address}") as resp:
            if resp.status == 200:
                data = await resp.json()
                balance = float(data.get("xrpBalance", 0))
        
        txs = []
        async with session.get(f"https://api.xrpscan.com/api/v1/account/{address}/transactions?limit=5") as resp:
            if resp.status == 200:
                data = await resp.json()
                txs = data.get("transactions", [])[:5]
        
        price = await getprice("ripple", session)
        return balance, txs, price, f"https://xrpscan.com/account/{address}"
    except:
        return None, [], 0, f"https://xrpscan.com/account/{address}"

async def fetchxrptx(txhash, session):
    try:
        tx = None
        async with session.get(f"https://api.xrpscan.com/api/v1/tx/{txhash}") as resp:
            if resp.status == 200:
                tx = await resp.json()
        
        price = await getprice("ripple", session)
        return tx, price, f"https://xrpscan.com/tx/{txhash}"
    except:
        return None, 0, f"https://xrpscan.com/tx/{txhash}"

async def fetchsol(address, session):
    try:
        balance = 0
        async with session.post("https://api.mainnet-beta.solana.com", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [address]
        }, headers={"User-Agent": "Mozilla/5.0"}) as resp:
            if resp.status == 200:
                data = await resp.json()
                balance = data.get("result", {}).get("value", 0) / 1e9
        
        sigs = []
        async with session.post("https://api.mainnet-beta.solana.com", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [address, {"limit": 5}]
        }, headers={"User-Agent": "Mozilla/5.0"}) as resp:
            if resp.status == 200:
                data = await resp.json()
                sigs = data.get("result", [])[:5]
        
        txs = []
        for sig in sigs[:5]:
            try:
                async with session.post("https://api.mainnet-beta.solana.com", json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTransaction",
                    "params": [sig["signature"], {"encoding": "json", "maxSupportedTransactionVersion": 0}]
                }, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                    if resp.status == 200:
                        txdata = await resp.json()
                        result = txdata.get("result")
                        if result:
                            txs.append(result)
            except Exception as e:
                continue
        
        price = await getprice("solana", session)
        return balance, txs, price, f"https://solscan.io/account/{address}"
    except Exception as e:
        return None, [], 0, f"https://solscan.io/account/{address}"

async def fetchsoltx(txhash, session):
    try:
        tx = None
        async with session.post("https://api.mainnet-beta.solana.com", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [txhash, {"encoding": "json", "maxSupportedTransactionVersion": 0}]
        }, headers={"User-Agent": "Mozilla/5.0"}) as resp:
            if resp.status == 200:
                data = await resp.json()
                tx = data.get("result")
        
        price = await getprice("solana", session)
        return tx, price, f"https://solscan.io/tx/{txhash}"
    except:
        return None, 0, f"https://solscan.io/tx/{txhash}"

async def execute(client, message):
    try:
        args = message.text.split(maxsplit=1)
        
        if len(args) < 2:
            await message.edit(await localise("usage: .trace [address or txid]"))
            return
        
        input = args[1].strip()
        
        if not input:
            await message.edit(await localise("address or txid cannot be empty"))
            return
        
        type = detect(input)
        
        if type == "unknown":
            await message.edit(await localise("unknown address or transaction format"))
            return
        
        try:
            await message.edit(await localise("tracing..."))
        except:
            pass
        
        try:
            import aiohttp
            timeout = aiohttp.ClientTimeout(total=120)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                if type == "eth_address":
                    balance, txs, price, link = await fetcheth(input, session)
                    
                    response = "ethereum address\n\n"
                    response += f"address: `{input}`\n"
                    if balance is not None:
                        usdval = balance * price
                        response += f"balance: {balance:.6f} eth (${usdval:.2f})\n"
                    else:
                        response += "balance: unavailable\n"
                    
                    response += f"\nrecent transactions ({len(txs)}):\n"
                    if txs and len(txs) > 0:
                        for i, tx in enumerate(txs[:5], 1):
                            try:
                                value = int(tx.get("value", 0)) / 1e18
                                usdval = value * price
                                confirms = tx.get("confirmations", "unknown")
                                timestamp = datetime.fromtimestamp(int(tx.get("timeStamp", 0))).strftime('%Y-%m-%d %H:%M:%S') if tx.get("timeStamp") else "unknown"
                                txhash = tx.get('hash', 'unknown')
                                fromaddr = tx.get('from', 'unknown')
                                toaddr = tx.get('to', 'unknown')
                                response += f"\n{i}. hash: `{txhash[:16]}...`\n"
                                response += f"   from: `{fromaddr[:10]}...`\n"
                                response += f"   to: `{toaddr[:10]}...`\n"
                                response += f"   value: {value:.6f} eth (${usdval:.2f})\n"
                                response += f"   confirmations: {confirms}\n"
                                response += f"   time: {timestamp}\n"
                                response += f"   link: https://etherscan.io/tx/{txhash}\n"
                            except Exception as e:
                                response += f"\n{i}. error parsing transaction\n"
                    else:
                        response += "no transactions found\n"
                    
                    response += f"\naddress link: {link}"
                    
                    if len(response) > 4096:
                        response = response[:4000] + f"\n\n...truncated\naddress link: {link}"
                    
                    await message.edit(response)
                
                elif type == "eth_tx":
                    tx, receipt, price, link = await fetchethtx(input, session)
                    
                    response = "ethereum transaction\n\n"
                    response += f"hash: `{input}`\n"
                    if tx:
                        response += f"from: `{tx.get('from', 'unknown')}`\n"
                        response += f"to: `{tx.get('to', 'unknown')}`\n"
                        value = int(tx.get('value', '0x0'), 16) / 1e18
                        usdval = value * price
                        response += f"value: {value:.6f} eth (${usdval:.2f})\n"
                        if receipt:
                            confirms = receipt.get("confirmations", "unknown")
                            response += f"confirmations: {confirms}\n"
                            response += f"status: {'success' if receipt.get('status') == '0x1' else 'failed'}\n"
                            response += f"block: {int(receipt.get('blockNumber', '0x0'), 16)}\n"
                    
                    response += f"\nlink: {link}"
                    await message.edit(response)
                
                elif type == "btc_address":
                    balance, txs, price, link = await fetchbtc(input, session)
                    
                    response = "bitcoin address\n\n"
                    response += f"address: `{input}`\n"
                    if balance is not None:
                        usdval = balance * price
                        response += f"balance: {balance:.8f} btc (${usdval:.2f})\n"
                    else:
                        response += "balance: unavailable\n"
                    
                    response += f"\nrecent transactions ({len(txs)}):\n"
                    if txs and len(txs) > 0:
                        for i, tx in enumerate(txs[:5], 1):
                            try:
                                value = sum([out.get("value", 0) for out in tx.get("out", [])]) / 1e8
                                usdval = value * price
                                confirms = tx.get("block_height", 0)
                                timestamp = datetime.fromtimestamp(tx.get("time", 0)).strftime('%Y-%m-%d %H:%M:%S') if tx.get("time") else "unknown"
                                txhash = tx.get('hash', 'unknown')
                                sender = tx.get("inputs", [{}])[0].get("prev_out", {}).get("addr", "unknown")
                                receiver = tx.get("out", [{}])[0].get("addr", "unknown")
                                
                                response += f"\n{i}. hash: `{txhash[:16]}...`\n"
                                response += f"   from: `{sender[:10]}...`\n"
                                response += f"   to: `{receiver[:10]}...`\n"
                                response += f"   value: {value:.8f} btc (${usdval:.2f})\n"
                                response += f"   confirmations: {confirms}\n"
                                response += f"   time: {timestamp}\n"
                                response += f"   link: https://blockchain.info/tx/{txhash}\n"
                            except Exception as e:
                                response += f"\n{i}. error parsing transaction\n"
                    else:
                        response += "no transactions found\n"
                    
                    response += f"\naddress link: {link}"
                    
                    if len(response) > 4096:
                        response = response[:4000] + f"\n\n...truncated\naddress link: {link}"
                    
                    await message.edit(response)
                
                elif type == "btc_tx":
                    tx, price, link = await fetchbtctx(input, session)
                    
                    response = "bitcoin transaction\n\n"
                    response += f"hash: `{input}`\n"
                    if tx:
                        value = sum([out.get("value", 0) for out in tx.get("out", [])]) / 1e8
                        usdval = value * price
                        sender = tx.get("inputs", [{}])[0].get("prev_out", {}).get("addr", "unknown")
                        receiver = tx.get("out", [{}])[0].get("addr", "unknown")
                        timestamp = datetime.fromtimestamp(tx.get("time", 0)).strftime('%Y-%m-%d %H:%M:%S') if tx.get("time") else "unknown"
                        
                        response += f"from: `{sender}`\n"
                        response += f"to: `{receiver}`\n"
                        response += f"value: {value:.8f} btc (${usdval:.2f})\n"
                        response += f"size: {tx.get('size', 0)} bytes\n"
                        response += f"confirmations: {tx.get('block_height', 0)}\n"
                        response += f"time: {timestamp}\n"
                    
                    response += f"\nlink: {link}"
                    await message.edit(response)
                
                elif type == "ltc_address":
                    balance, txs, price, link = await fetchltc(input, session)
                    
                    response = "litecoin address\n\n"
                    response += f"address: `{input}`\n"
                    if balance is not None:
                        usdval = balance * price
                        response += f"balance: {balance:.8f} ltc (${usdval:.2f})\n"
                    else:
                        response += "balance: unavailable\n"
                    
                    response += f"\nrecent transactions ({len(txs)}):\n"
                    if txs and len(txs) > 0:
                        for i, tx in enumerate(txs[:5], 1):
                            try:
                                txhash = tx.get("txid", "unknown")
                                
                                valuein = sum([vin.get("prevout", {}).get("value", 0) for vin in tx.get("vin", [])])
                                valueout = sum([vout.get("value", 0) for vout in tx.get("vout", [])])
                                value = valueout / 1e8
                                usdval = value * price
                                
                                confirms = tx.get("status", {}).get("block_height", 0)
                                timestamp = datetime.fromtimestamp(tx.get("status", {}).get("block_time", 0)).strftime('%Y-%m-%d %H:%M:%S') if tx.get("status", {}).get("block_time") else "unknown"
                                
                                vins = tx.get("vin", [])
                                vouts = tx.get("vout", [])
                                sender = vins[0].get("prevout", {}).get("scriptpubkey_address", "unknown") if vins and vins[0].get("prevout") else "coinbase"
                                receiver = vouts[0].get("scriptpubkey_address", "unknown") if vouts else "unknown"
                                
                                response += f"\n{i}. hash: `{txhash[:16]}...`\n"
                                response += f"   from: `{sender[:10]}...`\n"
                                response += f"   to: `{receiver[:10]}...`\n"
                                response += f"   value: {value:.8f} ltc (${usdval:.2f})\n"
                                response += f"   confirmations: {confirms}\n"
                                response += f"   time: {timestamp}\n"
                                response += f"   link: https://litecoinspace.org/tx/{txhash}\n"
                            except Exception as e:
                                response += f"\n{i}. error parsing transaction\n"
                    else:
                        response += "no transactions found\n"
                    
                    response += f"\naddress link: {link}"
                    
                    if len(response) > 4096:
                        response = response[:4000] + f"\n\n...truncated\naddress link: {link}"
                    
                    await message.edit(response)
                
                elif type == "ltc_tx":
                    tx, price, link = await fetchltctx(input, session)
                    
                    response = "litecoin transaction\n\n"
                    response += f"hash: `{input}`\n"
                    if tx:
                        valueout = sum([vout.get("value", 0) for vout in tx.get("vout", [])])
                        value = valueout / 1e8
                        usdval = value * price
                        
                        vins = tx.get("vin", [])
                        vouts = tx.get("vout", [])
                        sender = vins[0].get("prevout", {}).get("scriptpubkey_address", "unknown") if vins and vins[0].get("prevout") else "coinbase"
                        receiver = vouts[0].get("scriptpubkey_address", "unknown") if vouts else "unknown"
                        timestamp = datetime.fromtimestamp(tx.get("status", {}).get("block_time", 0)).strftime('%Y-%m-%d %H:%M:%S') if tx.get("status", {}).get("block_time") else "unknown"
                        
                        response += f"from: `{sender}`\n"
                        response += f"to: `{receiver}`\n"
                        response += f"value: {value:.8f} ltc (${usdval:.2f})\n"
                        response += f"size: {tx.get('size', 0)} bytes\n"
                        response += f"confirmations: {tx.get('status', {}).get('block_height', 0)}\n"
                        response += f"time: {timestamp}\n"
                    
                    response += f"\nlink: {link}"
                    await message.edit(response)
                
                elif type == "trx_address":
                    balance, txs, price, link = await fetchtrx(input, session)
                    
                    response = "tron address\n\n"
                    response += f"address: `{input}`\n"
                    if balance is not None:
                        usdval = balance * price
                        response += f"balance: {balance:.6f} trx (${usdval:.2f})\n"
                    else:
                        response += "balance: unavailable\n"
                    
                    response += f"\nrecent transactions ({len(txs)}):\n"
                    if txs and len(txs) > 0:
                        for i, tx in enumerate(txs[:5], 1):
                            try:
                                txhash = tx.get("hash", "unknown")
                                value = float(tx.get("amount", 0)) / 1e6
                                usdval = value * price
                                timestamp = datetime.fromtimestamp(tx.get("timestamp", 0) / 1000).strftime('%Y-%m-%d %H:%M:%S') if tx.get("timestamp") else "unknown"
                                response += f"\n{i}. hash: `{txhash[:16]}...`\n"
                                response += f"   value: {value:.6f} trx (${usdval:.2f})\n"
                                response += f"   status: {tx.get('contractRet', 'unknown')}\n"
                                response += f"   time: {timestamp}\n"
                                response += f"   link: https://tronscan.org/#/transaction/{txhash}\n"
                            except Exception as e:
                                response += f"\n{i}. error parsing transaction\n"
                    else:
                        response += "no transactions found\n"
                    
                    response += f"\naddress link: {link}"
                    
                    if len(response) > 4096:
                        response = response[:4000] + f"\n\n...truncated\naddress link: {link}"
                    
                    await message.edit(response)
                
                elif type == "trx_tx":
                    tx, price, link = await fetchtrxtx(input, session)
                    
                    response = "tron transaction\n\n"
                    response += f"hash: `{input}`\n"
                    if tx:
                        value = float(tx.get("amount", 0)) / 1e6
                        usdval = value * price
                        timestamp = datetime.fromtimestamp(tx.get("timestamp", 0) / 1000).strftime('%Y-%m-%d %H:%M:%S') if tx.get("timestamp") else "unknown"
                        
                        response += f"from: `{tx.get('ownerAddress', 'unknown')}`\n"
                        response += f"to: `{tx.get('toAddress', 'unknown')}`\n"
                        response += f"value: {value:.6f} trx (${usdval:.2f})\n"
                        response += f"status: {tx.get('contractRet', 'unknown')}\n"
                        response += f"time: {timestamp}\n"
                        response += f"confirmed: {tx.get('confirmed', False)}\n"
                    
                    response += f"\nlink: {link}"
                    await message.edit(response)
                
                elif type == "xrp_address":
                    balance, txs, price, link = await fetchxrp(input, session)
                    
                    response = "ripple address\n\n"
                    response += f"address: `{input}`\n"
                    if balance is not None:
                        usdval = balance * price
                        response += f"balance: {balance:.6f} xrp (${usdval:.2f})\n"
                    else:
                        response += "balance: unavailable\n"
                    
                    response += f"\nrecent transactions ({len(txs)}):\n"
                    if txs and len(txs) > 0:
                        for i, tx in enumerate(txs[:5], 1):
                            try:
                                txhash = tx.get("hash", "unknown")
                                value = float(tx.get("Amount", {}).get("value", 0)) if isinstance(tx.get("Amount"), dict) else float(tx.get("Amount", 0)) / 1e6
                                usdval = value * price
                                response += f"\n{i}. hash: `{txhash[:16]}...`\n"
                                response += f"   value: {value:.6f} xrp (${usdval:.2f})\n"
                                response += f"   status: {tx.get('result', 'unknown')}\n"
                                response += f"   link: https://xrpscan.com/tx/{txhash}\n"
                            except Exception as e:
                                response += f"\n{i}. error parsing transaction\n"
                    else:
                        response += "no transactions found\n"
                    
                    response += f"\naddress link: {link}"
                    
                    if len(response) > 4096:
                        response = response[:4000] + f"\n\n...truncated\naddress link: {link}"
                    
                    await message.edit(response)
                
                elif type == "xrp_tx":
                    tx, price, link = await fetchxrptx(input, session)
                    
                    response = "ripple transaction\n\n"
                    response += f"hash: `{input}`\n"
                    if tx:
                        value = float(tx.get("Amount", {}).get("value", 0)) if isinstance(tx.get("Amount"), dict) else float(tx.get("Amount", 0)) / 1e6
                        usdval = value * price
                        
                        response += f"from: `{tx.get('Account', 'unknown')}`\n"
                        response += f"to: `{tx.get('Destination', 'unknown')}`\n"
                        response += f"value: {value:.6f} xrp (${usdval:.2f})\n"
                        response += f"status: {tx.get('result', 'unknown')}\n"
                        response += f"ledger: {tx.get('ledger_index', 'unknown')}\n"
                    
                    response += f"\nlink: {link}"
                    await message.edit(response)
                
                elif type == "sol_address":
                    balance, txs, price, link = await fetchsol(input, session)
                    
                    response = "solana address\n\n"
                    response += f"address: `{input}`\n"
                    if balance is not None:
                        usdval = balance * price
                        response += f"balance: {balance:.6f} sol (${usdval:.2f})\n\n"
                    
                    if txs and len(txs) > 0:
                        response += "recent transactions:\n"
                        for tx in txs[:5]:
                            try:
                                if not tx:
                                    continue
                                meta = tx.get("meta", {})
                                sig = tx.get("transaction", {}).get("signatures", ["unknown"])[0]
                                
                                prebal = meta.get("preBalances", [0])[0] / 1e9
                                postbal = meta.get("postBalances", [0])[0] / 1e9
                                value = abs(postbal - prebal)
                                usdval = value * price
                                
                                response += f"\nhash: `{sig[:16]}...`\n"
                                response += f"value: {value:.6f} sol (${usdval:.2f})\n"
                                response += f"status: {'success' if meta.get('err') is None else 'failed'}\n"
                                response += f"link: https://solscan.io/tx/{sig}\n"
                            except Exception as e:
                                continue
                    
                    response += f"\naddress link: {link}"
                    await message.edit(response)
                
                elif type == "sol_tx":
                    tx, price, link = await fetchsoltx(input, session)
                    
                    response = "solana transaction\n\n"
                    response += f"hash: `{input}`\n"
                    if tx:
                        meta = tx.get("meta", {})
                        
                        prebal = meta.get("preBalances", [0])[0] / 1e9
                        postbal = meta.get("postBalances", [0])[0] / 1e9
                        value = abs(postbal - prebal)
                        usdval = value * price
                        
                        response += f"value: {value:.6f} sol (${usdval:.2f})\n"
                        response += f"status: {'success' if meta.get('err') is None else 'failed'}\n"
                        response += f"slot: {tx.get('slot', 'unknown')}\n"
                    
                    response += f"\nlink: {link}"
                    await message.edit(response)
                
                elif type == "generic_tx":
                    found = False
                    
                    btctx, btcprice, btclink = await fetchbtctx(input, session)
                    if btctx:
                        response = "bitcoin transaction\n\n"
                        response += f"hash: `{input}`\n"
                        value = sum([out.get("value", 0) for out in btctx.get("out", [])]) / 1e8
                        usdval = value * btcprice
                        sender = btctx.get("inputs", [{}])[0].get("prev_out", {}).get("addr", "unknown")
                        receiver = btctx.get("out", [{}])[0].get("addr", "unknown")
                        timestamp = datetime.fromtimestamp(btctx.get("time", 0)).strftime('%Y-%m-%d %H:%M:%S') if btctx.get("time") else "unknown"
                        
                        response += f"from: `{sender}`\n"
                        response += f"to: `{receiver}`\n"
                        response += f"value: {value:.8f} btc (${usdval:.2f})\n"
                        response += f"size: {btctx.get('size', 0)} bytes\n"
                        response += f"confirmations: {btctx.get('block_height', 0)}\n"
                        response += f"time: {timestamp}\n"
                        response += f"\nlink: {btclink}"
                        await message.edit(response)
                        found = True
                    
                    if not found:
                        ltctx, ltcprice, ltclink = await fetchltctx(input, session)
                        if ltctx and ltctx.get("txid"):
                            response = "litecoin transaction\n\n"
                            response += f"hash: `{input}`\n"
                            
                            valueout = sum([vout.get("value", 0) for vout in ltctx.get("vout", [])])
                            value = valueout / 1e8
                            usdval = value * ltcprice
                            
                            vins = ltctx.get("vin", [])
                            vouts = ltctx.get("vout", [])
                            sender = vins[0].get("prevout", {}).get("scriptpubkey_address", "unknown") if vins and vins[0].get("prevout") else "coinbase"
                            receiver = vouts[0].get("scriptpubkey_address", "unknown") if vouts else "unknown"
                            timestamp = datetime.fromtimestamp(ltctx.get("status", {}).get("block_time", 0)).strftime('%Y-%m-%d %H:%M:%S') if ltctx.get("status", {}).get("block_time") else "unknown"
                            
                            response += f"from: `{sender}`\n"
                            response += f"to: `{receiver}`\n"
                            response += f"value: {value:.8f} ltc (${usdval:.2f})\n"
                            response += f"size: {ltctx.get('size', 0)} bytes\n"
                            response += f"confirmations: {ltctx.get('status', {}).get('block_height', 0)}\n"
                            response += f"time: {timestamp}\n"
                            response += f"\nlink: {ltclink}"
                            await message.edit(response)
                            found = True
                    
                    if not found:
                        trxtx, trxprice, trxlink = await fetchtrxtx(input, session)
                        if trxtx and trxtx.get("hash"):
                            response = "tron transaction\n\n"
                            response += f"hash: `{input}`\n"
                            value = float(trxtx.get("amount", 0)) / 1e6
                            usdval = value * trxprice
                            timestamp = datetime.fromtimestamp(trxtx.get("timestamp", 0) / 1000).strftime('%Y-%m-%d %H:%M:%S') if trxtx.get("timestamp") else "unknown"
                            
                            response += f"from: `{trxtx.get('ownerAddress', 'unknown')}`\n"
                            response += f"to: `{trxtx.get('toAddress', 'unknown')}`\n"
                            response += f"value: {value:.6f} trx (${usdval:.2f})\n"
                            response += f"status: {trxtx.get('contractRet', 'unknown')}\n"
                            response += f"time: {timestamp}\n"
                            response += f"confirmed: {trxtx.get('confirmed', False)}\n"
                            response += f"\nlink: {trxlink}"
                            await message.edit(response)
                            found = True
                    
                    if not found:
                        xrptx, xrpprice, xrplink = await fetchxrptx(input, session)
                        if xrptx and xrptx.get("hash"):
                            response = "ripple transaction\n\n"
                            response += f"hash: `{input}`\n"
                            value = float(xrptx.get("Amount", {}).get("value", 0)) if isinstance(xrptx.get("Amount"), dict) else float(xrptx.get("Amount", 0)) / 1e6
                            usdval = value * xrpprice
                            
                            response += f"from: `{xrptx.get('Account', 'unknown')}`\n"
                            response += f"to: `{xrptx.get('Destination', 'unknown')}`\n"
                            response += f"value: {value:.6f} xrp (${usdval:.2f})\n"
                            response += f"status: {xrptx.get('result', 'unknown')}\n"
                            response += f"ledger: {xrptx.get('ledger_index', 'unknown')}\n"
                            response += f"\nlink: {xrplink}"
                            await message.edit(response)
                            found = True
                    
                    if not found:
                        await message.edit(await localise("transaction not found on btc, ltc, trx, or xrp networks"))
                
                elif type == "xmr_address":
                    response = "monero address\n\n"
                    response += f"address: `{input}`\n\n"
                    response += await localise("monero blockchain is private, balance lookup not available")
                    await message.edit(response)
                
                else:
                    response = f"{type}\n\n"
                    response += f"input: `{input}`\n"
                    response += await localise("detailed trace not yet implemented for this type")
                    await message.edit(response)
        except ImportError:
            await message.edit(await localise("aiohttp not installed"))
        except asyncio.TimeoutError:
            await message.edit(await localise("request timeout"))
        except Exception as e:
            await message.edit(await localise(f"trace failed: {str(e)}"))
    except Exception as e:
        try:
            await message.edit(await localise(f"error: {str(e)}"))
        except:
            try:
                await message.reply(await localise(f"critical error: {str(e)}"))
            except:
                pass
