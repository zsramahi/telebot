name = "ethereum"
aliases = ["eth"]
description = "show ethereum address"
category = "crypto"

import config
import re
import asyncio
import os

pending = {}

def validate(address):
    try:
        if not address or not isinstance(address, str):
            return False
        address = address.strip()
        if not re.match(r"^0x[a-fA-F0-9]{40}$", address):
            return False
        return True
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
                    if line.startswith("eth = "):
                        f.write(f'eth = "{address}"\n')
                        found = True
                    else:
                        f.write(line)
                if not found:
                    f.write(f'eth = "{address}"\n')
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
            if config.eth:
                try:
                    import aiohttp
                    timeout = aiohttp.ClientTimeout(total=10)
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        try:
                            async with session.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd") as resp:
                                if resp.status == 429:
                                    await message.edit(await localise(f"ethereum address: `{config.eth}`\nprice: rate limited"))
                                    return
                                elif resp.status != 200:
                                    await message.edit(await localise(f"ethereum address: `{config.eth}`\nprice: api error {resp.status}"))
                                    return
                                data = await resp.json()
                                price = data.get("ethereum", {}).get("usd", 0)
                                if price <= 0:
                                    await message.edit(await localise(f"ethereum address: `{config.eth}`\nprice: unavailable"))
                                    return
                            await message.edit(await localise(f"ethereum address: `{config.eth}`\nprice: ${price:.2f}"))
                        except asyncio.TimeoutError:
                            await message.edit(await localise(f"ethereum address: `{config.eth}`\nprice: timeout"))
                        except aiohttp.ClientError:
                            await message.edit(await localise(f"ethereum address: `{config.eth}`\nprice: network error"))
                        except Exception:
                            await message.edit(await localise(f"ethereum address: `{config.eth}`"))
                except ImportError:
                    await message.edit(await localise(f"ethereum address: `{config.eth}`\naiohttp not installed"))
                except Exception:
                    await message.edit(await localise(f"ethereum address: `{config.eth}`\nfailed to fetch price"))
            else:
                await message.edit(await localise('no address set. use ".eth [address]" to set your address'))
            return
        
        address = args[1].strip()
        
        if not address:
            await message.edit(await localise("address cannot be empty"))
            return
        
        if address.lower() in ["yes", "y"]:
            if userid in pending and pending[userid]["type"] == "eth":
                if pending[userid].get("expired", False):
                    await message.edit(await localise("no pending confirmation or expired"))
                    del pending[userid]
                    return
                    
                newaddr = pending[userid]["address"]
                config.eth = newaddr
                
                if not save(config.eth):
                    await message.edit(await localise("failed to save address"))
                    config.eth = pending[userid].get("old", None)
                    del pending[userid]
                    return
                
                oldmsg = pending[userid]["message"]
                del pending[userid]
                
                try:
                    await oldmsg.edit(await localise(f"current: `{config.eth}`\nnew: `{config.eth}`\n\nstatus: successful"))
                    await message.delete()
                except:
                    await message.edit(await localise(f"ethereum address set to: `{config.eth}`"))
            else:
                await message.edit(await localise("no pending confirmation or expired"))
            return
        
        if not validate(address):
            await message.edit(await localise("invalid ethereum address format"))
            return
        
        if config.eth:
            pending[userid] = {"type": "eth", "address": address, "message": message, "expired": False, "old": config.eth}
            await message.edit(await localise(f"current: `{config.eth}`\nnew: `{address}`\ntype .eth yes or .eth y within 60s to confirm\n\nstatus: pending"))
            
            asyncio.create_task(expire(userid, message))
        else:
            config.eth = address
            if not save(config.eth):
                await message.edit(await localise("failed to save address"))
                config.eth = None
                return
            await message.edit(await localise(f"ethereum address set to: `{config.eth}`"))
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
        if userid in pending and pending[userid]["type"] == "eth":
            pending[userid]["expired"] = True
            try:
                current = config.eth
                newaddr = pending[userid]["address"]
                await msg.edit(await localise(f"current: `{current}`\nnew: `{newaddr}`\ntype .eth yes or .eth y within 60s to confirm\n\nstatus: expired"))
            except:
                pass
    except:
        pass
