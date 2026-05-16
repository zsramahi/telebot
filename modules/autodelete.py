name = "autodelete"
description = "toggle auto delete messages"
category = "settings"

import config
import os

async def execute(client, message):
    try:
        oldstate = getattr(config, "autodelete", False)
        config.autodelete = not oldstate
        
        if not os.path.exists("config.py"):
            await message.edit(await localise("config file not found"))
            config.autodelete = oldstate
            return
        
        try:
            with open("config.py", "r", encoding="utf-8") as f:
                lines = f.readlines()
        except PermissionError:
            await message.edit(await localise("permission denied reading config"))
            config.autodelete = oldstate
            return
        except Exception as e:
            await message.edit(await localise(f"failed to read config: {str(e)}"))
            config.autodelete = oldstate
            return
        
        try:
            with open("config.py", "w", encoding="utf-8") as f:
                found = False
                for line in lines:
                    if line.startswith("autodelete = "):
                        f.write(f"autodelete = {config.autodelete}\n")
                        found = True
                    else:
                        f.write(line)
                if not found:
                    f.write(f"autodelete = {config.autodelete}\n")
        except PermissionError:
            await message.edit(await localise("permission denied writing config"))
            config.autodelete = oldstate
            return
        except IOError as e:
            await message.edit(await localise(f"io error saving config: {str(e)}"))
            config.autodelete = oldstate
            return
        except Exception as e:
            await message.edit(await localise(f"failed to save config: {str(e)}"))
            config.autodelete = oldstate
            return
        
        try:
            if config.autodelete:
                await message.edit(await localise("autodelete enabled (60s)"))
            else:
                await message.edit(await localise("autodelete disabled"))
        except:
            if config.autodelete:
                await message.reply(await localise("autodelete enabled (60s)"))
            else:
                await message.reply(await localise("autodelete disabled"))
    except Exception as e:
        try:
            await message.edit(await localise(f"error: {str(e)}"))
        except:
            try:
                await message.reply(await localise(f"critical error: {str(e)}"))
            except:
                pass
