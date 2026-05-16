name = "prefix"
description = "change command prefix"
category = "settings"

import config
import os

allowed = "!?,.@&£:/><~-_#%*+="

async def execute(client, message):
    try:
        args = message.text.split(maxsplit=1)
        
        if len(args) == 1:
            try:
                await message.edit(await localise(f"current prefix: `{config.prefix}`\nallowed: {allowed}"))
            except Exception as e:
                await message.reply(await localise(f"current prefix: `{config.prefix}`\nallowed: {allowed}"))
            return
        
        newprefix = args[1].strip()
        
        if not newprefix:
            await message.edit(await localise("prefix cannot be empty"))
            return
        
        if len(newprefix) != 1:
            await message.edit(await localise("prefix must be a single character"))
            return
        
        if newprefix not in allowed:
            await message.edit(await localise(f"invalid prefix. allowed: {allowed}"))
            return
        
        oldprefix = config.prefix
        config.prefix = newprefix
        
        if not os.path.exists("config.py"):
            await message.edit(await localise("config file not found"))
            config.prefix = oldprefix
            return
        
        try:
            with open("config.py", "r", encoding="utf-8") as f:
                lines = f.readlines()
        except PermissionError:
            await message.edit(await localise("permission denied reading config"))
            config.prefix = oldprefix
            return
        except Exception as e:
            await message.edit(await localise(f"failed to read config: {str(e)}"))
            config.prefix = oldprefix
            return
        
        try:
            with open("config.py", "w", encoding="utf-8") as f:
                found = False
                for line in lines:
                    if line.startswith("prefix = "):
                        f.write(f'prefix = "{config.prefix}"\n')
                        found = True
                    else:
                        f.write(line)
                if not found:
                    f.write(f'prefix = "{config.prefix}"\n')
        except PermissionError:
            await message.edit(await localise("permission denied writing config"))
            config.prefix = oldprefix
            return
        except IOError as e:
            await message.edit(await localise(f"io error saving config: {str(e)}"))
            config.prefix = oldprefix
            return
        except Exception as e:
            await message.edit(await localise(f"failed to save config: {str(e)}"))
            config.prefix = oldprefix
            return
        
        try:
            await message.edit(await localise(f"prefix changed to: `{config.prefix}`"))
        except:
            await message.reply(await localise(f"prefix changed to: `{config.prefix}`"))
    except Exception as e:
        try:
            await message.edit(await localise(f"error: {str(e)}"))
        except:
            try:
                await message.reply(await localise(f"critical error: {str(e)}"))
            except:
                pass
