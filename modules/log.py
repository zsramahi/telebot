name = "log"
description = "save chat history to file"
category = "general"

from datetime import datetime
import os

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
                await message.edit(await localise("invalid limit. use .log or .log [number]"))
                return
        
        await message.edit(await localise("logging chat history..."))
        
        messages = []
        try:
            async for msg in client.get_chat_history(message.chat.id, limit=limit):
                messages.append(msg)
        except Exception as e:
            await message.edit(await localise(f"failed to fetch messages: {str(e)}"))
            return
        
        messages.reverse()
        
        try:
            chat = await client.get_chat(message.chat.id)
            chatname = chat.title if chat.title else chat.first_name if chat.first_name else str(chat.id)
        except:
            chatname = str(message.chat.id)
        
        filename = f"log_{chatname}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"chat log: {chatname}\n")
                f.write(f"date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"total messages: {len(messages)}\n")
                f.write("=" * 50 + "\n\n")
                
                for msg in messages:
                    timestamp = msg.date.strftime('%Y-%m-%d %H:%M:%S') if msg.date else "unknown"
                    sender = "unknown"
                    
                    if msg.from_user:
                        sender = msg.from_user.first_name
                        if msg.from_user.username:
                            sender += f" (@{msg.from_user.username})"
                    
                    f.write(f"[{timestamp}] {sender}:\n")
                    
                    if msg.text:
                        f.write(f"{msg.text}\n")
                    
                    if msg.photo:
                        f.write(f"[photo: {msg.photo.file_id}]\n")
                    if msg.video:
                        f.write(f"[video: {msg.video.file_id}]\n")
                    if msg.document:
                        f.write(f"[document: {msg.document.file_name or msg.document.file_id}]\n")
                    if msg.audio:
                        f.write(f"[audio: {msg.audio.file_name or msg.audio.file_id}]\n")
                    if msg.voice:
                        f.write(f"[voice: {msg.voice.file_id}]\n")
                    if msg.sticker:
                        f.write(f"[sticker: {msg.sticker.emoji or 'sticker'}]\n")
                    if msg.animation:
                        f.write(f"[animation: {msg.animation.file_id}]\n")
                    
                    f.write("\n")
        except Exception as e:
            await message.edit(await localise(f"failed to write log file: {str(e)}"))
            return
        
        try:
            await client.send_document(message.chat.id, filename, caption=await localise(f"chat log: {len(messages)} messages"))
            await message.delete()
        except Exception as e:
            await message.edit(await localise(f"failed to send log: {str(e)}"))
            return
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
