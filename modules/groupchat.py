name = "groupchat"
aliases = ["gc"]
description = "create groupchat"
category = "general"

import config
from pyrogram.enums import ChatType

async def execute(client, message):
    try:
        try:
            with open("config.py", "r") as f:
                content = f.read()
        except Exception as e:
            await message.edit(await localise(f"failed to read config: {str(e)}"))
            return
        
        if "gccount = " in content:
            lines = content.split("\n")
            count = 0
            for line in lines:
                if line.startswith("gccount = "):
                    try:
                        count = int(line.split("=")[1].strip())
                    except:
                        count = 0
                    break
        else:
            count = 0
        
        count += 1
        
        try:
            users = []
            
            if message.chat.type == ChatType.PRIVATE:
                users = [message.chat.id]
            
            chat = await client.create_group(f"groupchat {count}", users)
            
            try:
                with open("config.py", "r") as f:
                    lines = f.readlines()
                
                with open("config.py", "w") as f:
                    found = False
                    for line in lines:
                        if line.startswith("gccount = "):
                            f.write(f"gccount = {count}\n")
                            found = True
                        else:
                            f.write(line)
                    if not found:
                        f.write(f"gccount = {count}\n")
            except Exception as e:
                await message.edit(await localise(f"group created but failed to save count: {str(e)}"))
                return
            
            await message.edit(await localise(f"created groupchat {count}"))
        except Exception as e:
            await message.edit(await localise(f"failed to create groupchat: {str(e)}"))
    except Exception as e:
        try:
            await message.edit(await localise(f"error: {str(e)}"))
        except:
            pass
