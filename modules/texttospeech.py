name = "texttospeech"
aliases = ["t2s", "tts"]
description = "text to speech"
category = "general"

import config
import re
import os
from gtts import gTTS

async def execute(client, message):
    try:
        text = message.text
        
        match = re.match(r'^.+?\s+["\u201c\u201d\'\u2018\u2019](.+)["\u201c\u201d\'\u2018\u2019]$', text)
        if not match:
            await message.edit(await localise('usage: .texttospeech "text"'))
            return
        
        spokentext = match.group(1)
        
        if not spokentext.strip():
            await message.edit(await localise("text cannot be empty"))
            return
        
        await message.edit(await localise("generating speech..."))
        
        lang = getattr(config, "language", "en")
        
        filename = "tts_output.mp3"
        
        try:
            tts = gTTS(text=spokentext, lang=lang)
            tts.save(filename)
        except Exception as e:
            await message.edit(await localise(f"failed to generate speech: {str(e)}"))
            return
        
        try:
            await client.send_voice(message.chat.id, filename)
            await message.delete()
        except Exception as e:
            await message.edit(await localise(f"failed to send voice: {str(e)}"))
        finally:
            try:
                if os.path.exists(filename):
                    os.remove(filename)
            except:
                pass
    except Exception as e:
        try:
            await message.edit(await localise(f"error: {str(e)}"))
        except:
            pass
