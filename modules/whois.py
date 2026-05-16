name = "whois"
aliases = ["info"]
description = "get user information"
category = "general"

from pyrogram.errors import FloodWait
import asyncio

async def execute(client, message):
    try:
        args = message.text.split(maxsplit=1)
        
        user = None
        
        if message.reply_to_message:
            if not message.reply_to_message.from_user:
                await message.edit(await localise("replied message has no user"))
                return
            user = message.reply_to_message.from_user
        elif len(args) > 1:
            username = args[1].strip().lstrip("@")
            if not username:
                await message.edit(await localise("invalid username"))
                return
            if len(username) > 32:
                await message.edit(await localise("username too long"))
                return
            try:
                user = await client.get_users(username)
            except FloodWait as e:
                await message.edit(await localise(f"rate limited, wait {e.value}s"))
                return
            except Exception as e:
                await message.edit(await localise(f"user not found: {str(e)}"))
                return
        else:
            try:
                user = await client.get_me()
            except FloodWait as e:
                await message.edit(await localise(f"rate limited, wait {e.value}s"))
                return
            except Exception as e:
                await message.edit(await localise(f"failed to get self info: {str(e)}"))
                return
        
        if not user:
            await message.edit(await localise("user not found"))
            return
        
        try:
            await message.edit(await localise("fetching user info..."))
        except:
            pass
        
        response = await localise("user information") + "\n\n"
        
        try:
            response += f"id: `{user.id}`\n"
            
            if user.first_name:
                response += f"first name: {user.first_name}\n"
            
            if user.last_name:
                response += f"last name: {user.last_name}\n"
            
            if user.username:
                response += f"username: @{user.username}\n"
            
            response += f"bot: {'yes' if user.is_bot else 'no'}\n"
            response += f"verified: {'yes' if user.is_verified else 'no'}\n"
            response += f"restricted: {'yes' if user.is_restricted else 'no'}\n"
            response += f"scam: {'yes' if user.is_scam else 'no'}\n"
            response += f"fake: {'yes' if user.is_fake else 'no'}\n"
            response += f"premium: {'yes' if user.is_premium else 'no'}\n"
            
            if user.phone_number:
                response += f"phone: +{user.phone_number}\n"
            
            if user.dc_id:
                response += f"datacenter: dc{user.dc_id}\n"
            
            if user.language_code:
                response += f"language: {user.language_code}\n"
            
            if user.status:
                try:
                    status = str(user.status).split(".")[-1].lower()
                    response += f"status: {status}\n"
                    
                    if hasattr(user.status, "date") and user.status.date:
                        response += f"last seen: {user.status.date}\n"
                except:
                    pass
        except Exception as e:
            await message.edit(await localise(f"error formatting user data: {str(e)}"))
            return
        
        try:
            photocount = 0
            async for _ in client.get_chat_photos(user.id):
                photocount += 1
                if photocount > 100:
                    break
            if photocount > 0:
                response += f"profile photos: {photocount}\n"
        except FloodWait as e:
            response += f"profile photos: rate limited\n"
        except:
            pass
        
        try:
            common = await client.get_common_chats(user.id)
            if common:
                response += f"common groups: {len(common)}\n"
        except FloodWait as e:
            response += f"common groups: rate limited\n"
        except:
            pass
        
        try:
            fulluser = await client.get_chat(user.id)
            if fulluser and fulluser.bio:
                response += f"\nbio:\n{fulluser.bio}\n"
        except FloodWait as e:
            response += f"\nbio: rate limited\n"
        except:
            pass
        
        response += f"\nlink: tg://user?id={user.id}"
        
        try:
            await message.edit(response)
        except Exception as e:
            try:
                await message.reply(response)
            except:
                await message.edit(await localise(f"failed to send response: {str(e)}"))
    except Exception as e:
        try:
            await message.edit(await localise(f"error: {str(e)}"))
        except:
            try:
                await message.reply(await localise(f"critical error: {str(e)}"))
            except:
                pass
