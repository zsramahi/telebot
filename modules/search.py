name = "search"
aliases = ["wiki"]
description = "search wikipedia"
category = "general"

import re
import asyncio

async def execute(client, message):
    try:
        text = message.text
        
        match = re.match(r'^.+?\s+["\u201c\u201d\'\u2018\u2019](.+)["\u201c\u201d\'\u2018\u2019]$', text)
        if not match:
            await message.edit(await localise('usage: .search "query"'))
            return
        
        query = match.group(1).strip()
        
        if not query:
            await message.edit(await localise("query cannot be empty"))
            return
        
        if len(query) > 300:
            await message.edit(await localise("query too long (max 300 chars)"))
            return
        
        try:
            await message.edit(await localise("searching wikipedia..."))
        except:
            pass
        
        try:
            import wikipedia
            
            try:
                wikipedia.set_lang("en")
                results = wikipedia.search(query, results=1)
                
                if not results or len(results) == 0:
                    await message.edit(await localise(f'no results found for "{query}"'))
                    return
                
                title = results[0]
                page = wikipedia.page(title, auto_suggest=False)
                
                summary = page.summary
                url = page.url
                
                maxlength = 3500
                if len(summary) > maxlength:
                    summary = summary[:maxlength] + "..."
                
                response = await localise("wikipedia search") + "\n\n"
                response += f"title: {page.title}\n\n"
                response += f"{summary}\n\n"
                response += f"link: {url}"
                
                try:
                    await message.edit(response)
                except Exception as e:
                    if len(response) > 4096:
                        response = response[:4000] + f"\n\nlink: {url}"
                        await message.edit(response)
                    else:
                        raise
            except wikipedia.exceptions.DisambiguationError as e:
                options = e.options[:5]
                response = await localise(f'"{query}" is ambiguous. options:\n')
                for opt in options:
                    response += f"- {opt}\n"
                await message.edit(response)
            except wikipedia.exceptions.PageError:
                await message.edit(await localise(f'no page found for "{query}"'))
            except asyncio.TimeoutError:
                await message.edit(await localise("request timeout"))
            except Exception as e:
                await message.edit(await localise(f"search failed: {str(e)}"))
        except ImportError:
            await message.edit(await localise("wikipedia package not installed"))
        except Exception as e:
            await message.edit(await localise(f"error searching wikipedia: {str(e)}"))
    except Exception as e:
        try:
            await message.edit(await localise(f"error: {str(e)}"))
        except:
            try:
                await message.reply(await localise(f"critical error: {str(e)}"))
            except:
                pass
