name = "afk"
description = "toggle afk mode"
category = "general"

import config
import re
import sys

defaultmsg = "hey there, im currently away from my device and will be back soon to help you."

def save(msg):
    try:
        with open("config.py", "r") as f:
            lines = f.readlines()
        
        with open("config.py", "w") as f:
            found = False
            for line in lines:
                if line.startswith("afkmessage = "):
                    f.write(f'afkmessage = "{msg}"\n')
                    found = True
                else:
                    f.write(line)
            if not found:
                f.write(f'afkmessage = "{msg}"\n')
        return True
    except:
        return False

async def execute(client, message):
    try:
        initmodule = sys.modules['__main__']
        text = message.text
        
        if not hasattr(config, "afkmessage"):
            config.afkmessage = defaultmsg
        
        if text.strip() == ".afk":
            initmodule.afkenabled = not initmodule.afkenabled
            
            if initmodule.afkenabled:
                await message.edit(await localise(f"afk mode enabled\nmessage: {config.afkmessage}"))
            else:
                await message.edit(await localise("afk mode disabled"))
            return
        
        arg = text[4:].strip()
        
        if arg.lower() == "reset":
            config.afkmessage = defaultmsg
            if not save(config.afkmessage):
                await message.edit(await localise("failed to save afk message"))
                return
            await message.edit(await localise(f"afk message reset to default\nmessage: {config.afkmessage}"))
            return
        
        match = re.match(r'^["\u201c\u201d\'\u2018\u2019](.+)["\u201c\u201d\'\u2018\u2019]$', arg)
        if match:
            newmsg = match.group(1)
            if not newmsg.strip():
                await message.edit(await localise("message cannot be empty"))
                return
            config.afkmessage = newmsg
            if not save(config.afkmessage):
                await message.edit(await localise("failed to save afk message"))
                return
            await message.edit(await localise(f"afk message updated\nmessage: {config.afkmessage}"))
        else:
            await message.edit(await localise('invalid format. use .afk "message" with quotes'))
    except Exception as e:
        try:
            await message.edit(await localise(f"error: {str(e)}"))
        except:
            pass
