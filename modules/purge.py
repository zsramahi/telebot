name = "purge"
aliases = ["delete"]
description = "delete messages"
category = "general"

from pyrogram.enums import ChatType
import asyncio

async def execute(client, message):
    try:
        args = message.text.split(maxsplit=1)
        
        limit = None
        if len(args) > 1:
            try:
                limit = int(args[1])
                if limit <= 0:
                    await message.edit(await localise("limit must be positive"))
                    return
            except ValueError:
                await message.edit(await localise("invalid limit. use .purge or .purge [number]"))
                return
        
        try:
            chat = await client.get_chat(message.chat.id)
            me = await client.get_me()
        except Exception as e:
            await message.edit(await localise(f"failed to get chat info: {str(e)}"))
            return
        
        candeleteall = False
        
        if chat.type == ChatType.PRIVATE:
            candeleteall = True
        elif chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            try:
                member = await client.get_chat_member(message.chat.id, me.id)
                if member.status in ["creator", "administrator"]:
                    permissions = member.privileges
                    if permissions and permissions.can_delete_messages:
                        candeleteall = True
            except:
                pass
        
        todelete = []
        count = 0
        
        try:
            async for msg in client.get_chat_history(message.chat.id, limit=limit):
                if candeleteall:
                    todelete.append(msg.id)
                    count += 1
                else:
                    if msg.from_user and msg.from_user.id == me.id:
                        todelete.append(msg.id)
                        count += 1
        except Exception as e:
            await message.edit(await localise(f"failed to fetch messages: {str(e)}"))
            return
        
        if todelete:
            try:
                await client.delete_messages(message.chat.id, todelete)
            except Exception as e:
                await message.edit(await localise(f"failed to delete messages: {str(e)}"))
                return
        
        status = await client.send_message(message.chat.id, await localise(f"deleted {count} messages"))
        
        await asyncio.sleep(2)
        try:
            await status.delete()
        except:
            pass
    except Exception as e:
        try:
            await message.edit(await localise(f"error: {str(e)}"))
        except:
            pass
