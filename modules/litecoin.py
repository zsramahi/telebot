name = "litecoin"
aliases = ["ltc"]
description = "show litecoin address"
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
        if address.startswith("L") or address.startswith("M") or address.startswith("ltc1"):
            if address.startswith("ltc1"):
                return len(address) >= 43 and len(address) <= 90 and address.islower()
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
                    if line.startswith("ltc = "):
                        f.write(f'ltc = "{address}"\n')
                        found = True
                    else:
                        f.write(line)
                if not found:
                    f.write(f'ltc = "{address}"\n')
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
            if config.ltc:
                try:
                    import aiohttp
                    timeout = aiohttp.ClientTimeout(total=10)
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        try:
                            async with session.get("https://api.coingecko.com/api/v3/simple/price?ids=litecoin&vs_currencies=usd") as resp:
                                if resp.status == 429:
                                    await message.edit(await localise(f"litecoin address: `{config.ltc}`\nprice: rate limited"))
                                    return
                                elif resp.status != 200:
                                    await message.edit(await localise(f"litecoin address: `{config.ltc}`\nprice: api error {resp.status}"))
                                    return
                                data = await resp.json()
                                price = data.get("litecoin", {}).get("usd", 0)
                                if price <= 0:
                                    await message.edit(await localise(f"litecoin address: `{config.ltc}`\nprice: unavailable"))
                                    return
                            await message.edit(await localise(f"litecoin address: `{config.ltc}`\nprice: ${price:.2f}"))
                        except asyncio.TimeoutError:
                            await message.edit(await localise(f"litecoin address: `{config.ltc}`\nprice: timeout"))
                        except aiohttp.ClientError:
                            await message.edit(await localise(f"litecoin address: `{config.ltc}`\nprice: network error"))
                        except Exception:
                            await message.edit(await localise(f"litecoin address: `{config.ltc}`"))
                except ImportError:
                    await message.edit(await localise(f"litecoin address: `{config.ltc}`\naiohttp not installed"))
                except Exception:
                    await message.edit(await localise(f"litecoin address: `{config.ltc}`\nfailed to fetch price"))
            else:
                await message.edit(await localise('no address set. use ".ltc [address]" to set your address'))
            return
        
        address = args[1].strip()
        
        if not address:
            await message.edit(await localise("address cannot be empty"))
            return
        
        if address.lower() in ["yes", "y"]:
            if userid in pending and pending[userid]["type"] == "ltc":
                if pending[userid].get("expired", False):
                    await message.edit(await localise("no pending confirmation or expired"))
                    del pending[userid]
                    return
                    
                newaddr = pending[userid]["address"]
                config.ltc = newaddr
                
                if not save(config.ltc):
                    await message.edit(await localise("failed to save address"))
                    config.ltc = pending[userid].get("old", None)
                    del pending[userid]
                    return
                
                oldmsg = pending[userid]["message"]
                del pending[userid]
                
                try:
                    await oldmsg.edit(await localise(f"current: `{config.ltc}`\nnew: `{config.ltc}`\n\nstatus: successful"))
                    await message.delete()
                except:
                    await message.edit(await localise(f"litecoin address set to: `{config.ltc}`"))
            else:
                await message.edit(await localise("no pending confirmation or expired"))
            return
        
        if not validate(address):
            await message.edit(await localise("invalid litecoin address format"))
            return
        
        if config.ltc:
            pending[userid] = {"type": "ltc", "address": address, "message": message, "expired": False, "old": config.ltc}
            await message.edit(await localise(f"current: `{config.ltc}`\nnew: `{address}`\ntype .ltc yes or .ltc y within 60s to confirm\n\nstatus: pending"))
            
            asyncio.create_task(expire(userid, message))
        else:
            config.ltc = address
            if not save(config.ltc):
                await message.edit(await localise("failed to save address"))
                config.ltc = None
                return
            await message.edit(await localise(f"litecoin address set to: `{config.ltc}`"))
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
        if userid in pending and pending[userid]["type"] == "ltc":
            pending[userid]["expired"] = True
            try:
                current = config.ltc
                newaddr = pending[userid]["address"]
                await msg.edit(await localise(f"current: `{current}`\nnew: `{newaddr}`\ntype .ltc yes or .ltc y within 60s to confirm\n\nstatus: expired"))
            except:
                pass
    except:
        pass
