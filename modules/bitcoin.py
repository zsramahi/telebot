name = "bitcoin"
aliases = ["btc"]
description = "show bitcoin address"
category = "crypto"

import config
import asyncio
import os

pending = {}

def validate(address):
    try:
        if not address or not isinstance(address, str):
            return False
        address = address.strip()
        if len(address) < 26 or len(address) > 90:
            return False
        if address.startswith("1") or address.startswith("3") or address.startswith("bc1"):
            if address.startswith("bc1"):
                return len(address) >= 42 and len(address) <= 90 and address.islower()
            return len(address) >= 26 and len(address) <= 35
        return False
    except:
        return False

def save(address):
    try:
        if not os.path.exists("config.py"):
            return False
        
        try:
            with open("config.py", "r", encoding="utf-8") as f:
                lines = f.readlines()
        except PermissionError:
            return False
        except Exception:
            return False
        
        try:
            with open("config.py", "w", encoding="utf-8") as f:
                found = False
                for line in lines:
                    if line.startswith("btc = "):
                        f.write(f'btc = "{address}"\n')
                        found = True
                    else:
                        f.write(line)
                if not found:
                    f.write(f'btc = "{address}"\n')
            return True
        except PermissionError:
            return False
        except IOError:
            return False
        except Exception:
            return False
    except:
        return False

async def execute(client, message):
    try:
        args = message.text.split(maxsplit=1)
        
        if not message.from_user:
            await message.edit(await localise("cannot identify user"))
            return
        
        userid = message.from_user.id
        
        if len(args) == 1:
            if config.btc:
                try:
                    import aiohttp
                    timeout = aiohttp.ClientTimeout(total=10)
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        try:
                            async with session.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd") as resp:
                                if resp.status == 429:
                                    await message.edit(await localise(f"bitcoin address: `{config.btc}`\nprice: rate limited"))
                                    return
                                elif resp.status != 200:
                                    await message.edit(await localise(f"bitcoin address: `{config.btc}`\nprice: api error {resp.status}"))
                                    return
                                data = await resp.json()
                                price = data.get("bitcoin", {}).get("usd", 0)
                                if price <= 0:
                                    await message.edit(await localise(f"bitcoin address: `{config.btc}`\nprice: unavailable"))
                                    return
                            await message.edit(await localise(f"bitcoin address: `{config.btc}`\nprice: ${price:.2f}"))
                        except asyncio.TimeoutError:
                            await message.edit(await localise(f"bitcoin address: `{config.btc}`\nprice: timeout"))
                        except aiohttp.ClientError as e:
                            await message.edit(await localise(f"bitcoin address: `{config.btc}`\nprice: network error"))
                        except Exception:
                            await message.edit(await localise(f"bitcoin address: `{config.btc}`"))
                except ImportError:
                    await message.edit(await localise(f"bitcoin address: `{config.btc}`\naiohttp not installed"))
                except Exception as e:
                    await message.edit(await localise(f"bitcoin address: `{config.btc}`\nfailed to fetch price"))
            else:
                await message.edit(await localise('no address set. use ".btc [address]" to set your address'))
            return
        
        address = args[1].strip()
        
        if not address:
            await message.edit(await localise("address cannot be empty"))
            return
        
        if address.lower() in ["yes", "y"]:
            if userid in pending and pending[userid]["type"] == "btc":
                if pending[userid].get("expired", False):
                    await message.edit(await localise("no pending confirmation or expired"))
                    del pending[userid]
                    return
                    
                newaddr = pending[userid]["address"]
                config.btc = newaddr
                
                if not save(config.btc):
                    await message.edit(await localise("failed to save address"))
                    config.btc = pending[userid].get("old", None)
                    del pending[userid]
                    return
                
                oldmsg = pending[userid]["message"]
                del pending[userid]
                
                try:
                    await oldmsg.edit(await localise(f"current: `{config.btc}`\nnew: `{config.btc}`\n\nstatus: successful"))
                    await message.delete()
                except:
                    await message.edit(await localise(f"bitcoin address set to: `{config.btc}`"))
            else:
                await message.edit(await localise("no pending confirmation or expired"))
            return
        
        if not validate(address):
            await message.edit(await localise("invalid bitcoin address format"))
            return
        
        if config.btc:
            pending[userid] = {"type": "btc", "address": address, "message": message, "expired": False, "old": config.btc}
            await message.edit(await localise(f"current: `{config.btc}`\nnew: `{address}`\ntype .btc yes or .btc y within 60s to confirm\n\nstatus: pending"))
            
            asyncio.create_task(expire(userid, message))
        else:
            config.btc = address
            if not save(config.btc):
                await message.edit(await localise("failed to save address"))
                config.btc = None
                return
            await message.edit(await localise(f"bitcoin address set to: `{config.btc}`"))
    except Exception as e:
        try:
            await message.edit(await localise(f"error: {str(e)}"))
        except:
            try:
                await message.reply(await localise(f"critical error: {str(e)}"))
            except:
                pass

async def expire(userid, msg):
    try:
        await asyncio.sleep(60)
        if userid in pending and pending[userid]["type"] == "btc":
            pending[userid]["expired"] = True
            try:
                current = config.btc
                newaddr = pending[userid]["address"]
                await msg.edit(await localise(f"current: `{current}`\nnew: `{newaddr}`\ntype .btc yes or .btc y within 60s to confirm\n\nstatus: expired"))
            except:
                pass
    except:
        pass
