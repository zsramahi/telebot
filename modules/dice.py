name = "dice"
description = "roll a dice"
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
            dice = await client.send_dice(message.chat.id, "🎲")
        except FloodWait as e:
            await client.send_message(message.chat.id, await localise(f"rate limited, wait {e.value}s"))
            return
        except ChatWriteForbidden:
            return
        except Exception as e:
            await client.send_message(message.chat.id, await localise(f"failed to send dice: {str(e)}"))
            return
        
        if not dice or not dice.dice:
            await client.send_message(message.chat.id, await localise("dice result unavailable"))
            return
        
        try:
            await asyncio.sleep(5)
        except:
            pass
        
        try:
            await client.send_message(message.chat.id, await localise(f"rolled: {dice.dice.value}"))
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
