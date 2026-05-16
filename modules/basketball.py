name = "basketball"
aliases = ["bb"]
description = "shoot a basketball"
category = "games"

import asyncio
from pyrogram.errors import FloodWait, ChatWriteForbidden, MessageDeleteForbidden

async def execute(client, message):
    try:
        try:
            await message.delete()
        except MessageDeleteForbidden:
            await message.edit(await localise("cannot delete message"))
            return
        except Exception:
            pass
        
        try:
            dice = await client.send_dice(message.chat.id, "🏀")
        except FloodWait as e:
            await client.send_message(message.chat.id, await localise(f"rate limited, wait {e.value}s"))
            return
        except ChatWriteForbidden:
            return
        except Exception as e:
            await client.send_message(message.chat.id, await localise(f"failed to send basketball: {str(e)}"))
            return
        
        if not dice or not dice.dice:
            await client.send_message(message.chat.id, await localise("basketball result unavailable"))
            return
        
        try:
            await asyncio.sleep(6)
        except:
            pass
        
        results = {
            1: "miss",
            2: "miss", 
            3: "miss",
            4: "score",
            5: "score"
        }
        
        result = results.get(dice.dice.value, "stuck")
        
        try:
            await client.send_message(message.chat.id, await localise(f"result: {result}"))
        except FloodWait as e:
            pass
        except ChatWriteForbidden:
            pass
        except Exception:
            pass
    except Exception as e:
        try:
            await message.edit(await localise(f"error: {str(e)}"))
        except:
            try:
                await message.reply(await localise(f"critical error: {str(e)}"))
            except:
                pass
