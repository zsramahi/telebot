name = "language"
description = "set language for tts and translate"
category = "settings"

import config
import os

languages = {
    "english": "en",
    "russian": "ru",
    "hindi": "hi",
    "urdu": "ur",
    "polish": "pl",
    "spanish": "es",
    "italian": "it",
    "romanian": "ro",
    "french": "fr"
}

async def execute(client, message):
    try:
        args = message.text.split(maxsplit=1)
        
        if len(args) == 1:
            try:
                current = [k for k, v in languages.items() if v == config.language][0] if config.language in languages.values() else "english"
                langlist = ", ".join(languages.keys())
                await message.edit(await localise(f"current language: {current}\navailable: {langlist}"))
            except Exception as e:
                await message.reply(await localise(f"current language: {getattr(config, 'language', 'en')}\navailable: {', '.join(languages.keys())}"))
            return
        
        lang = args[1].strip().lower()
        
        if not lang:
            await message.edit(await localise("language cannot be empty"))
            return
        
        if lang not in languages:
            await message.edit(await localise(f"invalid language. available: {', '.join(languages.keys())}"))
            return
        
        oldlang = config.language
        config.language = languages[lang]
        
        if not os.path.exists("config.py"):
            await message.edit(await localise("config file not found"))
            config.language = oldlang
            return
        
        try:
            with open("config.py", "r", encoding="utf-8") as f:
                lines = f.readlines()
        except PermissionError:
            await message.edit(await localise("permission denied reading config"))
            config.language = oldlang
            return
        except Exception as e:
            await message.edit(await localise(f"failed to read config: {str(e)}"))
            config.language = oldlang
            return
        
        try:
            with open("config.py", "w", encoding="utf-8") as f:
                found = False
                for line in lines:
                    if line.startswith("language = "):
                        f.write(f'language = "{config.language}"\n')
                        found = True
                    else:
                        f.write(line)
                if not found:
                    f.write(f'language = "{config.language}"\n')
        except PermissionError:
            await message.edit(await localise("permission denied writing config"))
            config.language = oldlang
            return
        except IOError as e:
            await message.edit(await localise(f"io error saving config: {str(e)}"))
            config.language = oldlang
            return
        except Exception as e:
            await message.edit(await localise(f"failed to save config: {str(e)}"))
            config.language = oldlang
            return
        
        try:
            await message.edit(await localise(f"language set to: {lang}"))
        except:
            await message.reply(await localise(f"language set to: {lang}"))
    except Exception as e:
        try:
            await message.edit(await localise(f"error: {str(e)}"))
        except:
            try:
                await message.reply(await localise(f"critical error: {str(e)}"))
            except:
                pass
