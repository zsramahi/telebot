name = "ping"
description = "check response time"
category = "general"

import time

async def execute(client, message):
    try:
        start = time.perf_counter()
        try:
            await message.edit(await localise("pinging..."))
        except Exception as e:
            await message.reply(await localise(f"failed to edit message: {str(e)}"))
            return
        end = time.perf_counter()
        ms = (end - start) * 1000
        
        if ms < 0:
            await message.edit(await localise("invalid timing result"))
            return
        
        try:
            await message.edit(await localise(f"pong: {ms:.2f}ms"))
        except Exception as e:
            await message.reply(await localise(f"pong: {ms:.2f}ms (edit failed)"))
    except OverflowError:
        try:
            await message.edit(await localise("timing overflow error"))
        except:
            pass
    except Exception as e:
        try:
            await message.edit(await localise(f"error: {str(e)}"))
        except:
            try:
                await message.reply(await localise(f"critical error: {str(e)}"))
            except:
                pass
