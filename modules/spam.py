name = "spam"
description = "spam messages"
category = "general"

import re
import asyncio

spamming = False

async def execute(client, message):
    try:
        global spamming
        text = message.text
        
        if text.strip() == ".spam stop":
            spamming = False
            await message.edit(await localise("spam stopped"))
            return
        
        match = re.match(r'^\.spam\s+["\u201c\u201d\'\u2018\u2019](.+)["\u201c\u201d\'\u2018\u2019]\s+(\d+)$', text)
        if not match:
            await message.edit(await localise('usage: .spam "text" [count] or .spam stop'))
            return
        
        spamtext = match.group(1)
        try:
            count = int(match.group(2))
        except ValueError:
            await message.edit(await localise("invalid count"))
            return
        
        if count <= 0:
            await message.edit(await localise("count must be positive"))
            return
        
        if count > 500:
            await message.edit(await localise("max 500 messages"))
            return
        
        try:
            await message.delete()
        except:
            pass
        
        spamming = True
        for i in range(count):
            if not spamming:
                break
            try:
                await client.send_message(message.chat.id, spamtext)
                await asyncio.sleep(0.1)
            except Exception as e:
                spamming = False
                try:
                    await client.send_message(message.chat.id, await localise(f"spam failed at {i+1}/{count}: {str(e)}"))
                except:
                    pass
                break
        
        spamming = False
    except Exception as e:
        try:
            await message.edit(await localise(f"error: {str(e)}"))
        except:
            pass
