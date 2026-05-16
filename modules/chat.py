name = "chat"
aliases = ["ai", "ask"]
description = "chat with ai assistant"
category = "general"

import re
import asyncio

history = []

async def execute(client, message):
    try:
        text = message.text
        
        stream = text.endswith(" --stream")
        if stream:
            text = text[:-9].strip()
        
        match = re.match(r'^.+?\s+["\u201c\u201d](.+)["\u201c\u201d]$', text)
        if not match:
            match = re.match(r"^.+?\s+['\u2018\u2019](.+)['\u2018\u2019]$", text)
        if not match:
            parts = text.split(maxsplit=1)
            if len(parts) < 2:
                await message.edit(await localise('usage: .chat query or .chat "query"'))
                return
            query = parts[1].strip()
        else:
            query = match.group(1).strip()
        
        if not query:
            await message.edit(await localise("query cannot be empty"))
            return
        
        if len(query) > 2000:
            await message.edit(await localise("query too long (max 2000 chars)"))
            return
        
        try:
            await message.edit(await localise("thinking..."))
        except:
            pass
        
        try:
            import aiohttp
            import config
            
            apikey = config.openrouterapikey
            model = "nvidia/nemotron-3-nano-30b-a3b:free"
            
            headers = {
                "Authorization": f"Bearer {apikey}",
                "Content-Type": "application/json"
            }
            
            messages = []
            messages.append({"role": "system", "content": "you are a helpful assistant. keep responses concise and brief. avoid long explanations unless specifically asked."})
            for msg in history:
                messages.append(msg)
            messages.append({"role": "user", "content": query})
            
            payload = {
                "model": model,
                "messages": messages,
                "stream": stream
            }
            
            timeout = aiohttp.ClientTimeout(total=120)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                try:
                    async with session.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload) as resp:
                        if resp.status == 429:
                            await message.edit(await localise("rate limited"))
                            return
                        elif resp.status == 401:
                            await message.edit(await localise("invalid api key"))
                            return
                        elif resp.status != 200:
                            await message.edit(await localise(f"api error {resp.status}"))
                            return
                        
                        reply = ""
                        
                        if stream:
                            lastupdate = 0
                            updatecount = 0
                            lastreply = ""
                            
                            async for line in resp.content:
                                try:
                                    decoded = line.decode('utf-8').strip()
                                    if not decoded or not decoded.startswith("data: "):
                                        continue
                                    
                                    jsonstr = decoded[6:]
                                    if jsonstr == "[DONE]":
                                        break
                                    
                                    import json
                                    chunk = json.loads(jsonstr)
                                    
                                    if "choices" in chunk and len(chunk["choices"]) > 0:
                                        delta = chunk["choices"][0].get("delta", {})
                                        content = delta.get("content", "")
                                        if content:
                                            reply += content
                                            updatecount += 1
                                            
                                            import time
                                            now = time.time()
                                            if updatecount >= 20 or now - lastupdate > 3:
                                                try:
                                                    response = f"query: {query}\n\n{reply}"
                                                    if len(response) > 4090:
                                                        response = response[:4090] + "..."
                                                    if response != lastreply:
                                                        await message.edit(response)
                                                        lastreply = response
                                                    lastupdate = now
                                                    updatecount = 0
                                                except Exception as e:
                                                    if "MESSAGE_NOT_MODIFIED" not in str(e):
                                                        pass
                                except:
                                    continue
                        else:
                            data = await resp.json()
                            
                            if not data or "choices" not in data:
                                await message.edit(await localise("invalid response"))
                                return
                            
                            choices = data.get("choices", [])
                            if not choices or len(choices) == 0:
                                await message.edit(await localise("no response generated"))
                                return
                            
                            reply = choices[0].get("message", {}).get("content", "")
                        
                        if not reply:
                            await message.edit(await localise("empty response"))
                            return
                        
                        history.append({"role": "user", "content": query})
                        history.append({"role": "assistant", "content": reply})
                        
                        maxlength = 4000
                        if len(reply) > maxlength:
                            reply = reply[:maxlength] + "..."
                        
                        response = f"query: {query}\n\n{reply}"
                        
                        try:
                            if stream:
                                if response != lastreply:
                                    await message.edit(response)
                            else:
                                await message.edit(response)
                        except Exception as e:
                            if "MESSAGE_NOT_MODIFIED" not in str(e):
                                if len(response) > 4096:
                                    response = response[:4090] + "..."
                                    await message.edit(response)
                                else:
                                    raise
                except asyncio.TimeoutError:
                    await message.edit(await localise("request timeout"))
                except aiohttp.ClientError:
                    await message.edit(await localise("network error"))
                except ValueError:
                    await message.edit(await localise("invalid response data"))
                except Exception as e:
                    await message.edit(await localise(f"chat failed: {str(e)}"))
        except ImportError:
            await message.edit(await localise("aiohttp not installed"))
        except Exception as e:
            await message.edit(await localise(f"error: {str(e)}"))
    except Exception as e:
        try:
            await message.edit(await localise(f"error: {str(e)}"))
        except:
            try:
                await message.reply(await localise(f"critical error: {str(e)}"))
            except:
                pass
