name = "translate"
description = "translate text"
category = "general"

import config
import re
from googletrans import Translator

translator = Translator()

async def execute(client, message):
    try:
        text = message.text
        targetlang = getattr(config, "language", "en")
        
        sourcetext = None
        
        if message.reply_to_message:
            sourcetext = message.reply_to_message.text
            if not sourcetext:
                await message.edit(await localise("no text to translate"))
                return
        else:
            match = re.match(r'^.+?\s+["\u201c\u201d\'\u2018\u2019](.+)["\u201c\u201d\'\u2018\u2019]$', text)
            if not match:
                await message.edit(await localise('usage: .translate "text" or reply to message'))
                return
            sourcetext = match.group(1)
        
        if not sourcetext.strip():
            await message.edit(await localise("text cannot be empty"))
            return
        
        await message.edit(await localise("translating..."))
        
        try:
            result = await translator.translate(sourcetext, dest=targetlang)
            
            if not result or not result.text:
                await message.edit(await localise("translation failed"))
                return
            
            response = f"translated to {targetlang}:\n\n{result.text}"
            if result.src and result.src != "auto":
                response = f"from {result.src} " + response
            
            await message.edit(response)
        except Exception as e:
            await message.edit(await localise(f"translation error: {str(e)}"))
    except Exception as e:
        try:
            await message.edit(await localise(f"error: {str(e)}"))
        except:
            pass
