name = "help"
aliases = ["cmds", "cmd", "commands", "command"]
description = "shows all available commands"
category = "settings"

import config

async def execute(client, message):
    try:
        from pathlib import Path
        import importlib.util
        
        moduledir = Path(__file__).parent
        categories = {}
        seen = set()
        
        try:
            for file in moduledir.glob("*.py"):
                if file.name.startswith("_"):
                    continue
                
                try:
                    spec = importlib.util.spec_from_file_location(file.stem, file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    if hasattr(module, "name") and hasattr(module, "description"):
                        if module.name in seen:
                            continue
                        seen.add(module.name)
                        
                        cat = getattr(module, "category", "other")
                        if cat not in categories:
                            categories[cat] = []
                        
                        cmdtext = f"{getattr(config, 'prefix', '.')}{module.name}"
                        if hasattr(module, "aliases") and module.aliases:
                            aliasstr = ", ".join([f"{getattr(config, 'prefix', '.')}{a}" for a in module.aliases])
                            cmdtext += f" ({aliasstr})"
                        cmdtext += f" - {await localise(module.description)}"
                        
                        categories[cat].append(cmdtext)
                except:
                    continue
        except Exception as e:
            await message.edit(await localise(f"failed to load modules: {str(e)}"))
            return
        
        categoryorder = ["general", "games", "crypto", "settings"]
        response = await localise("available commands:") + "\n\n"
        
        for cat in categoryorder:
            if cat in categories:
                response += await localise(cat) + ":\n"
                response += "\n".join(sorted(categories[cat])) + "\n\n"
        
        for cat in sorted(categories.keys()):
            if cat not in categoryorder:
                response += await localise(cat) + ":\n"
                response += "\n".join(sorted(categories[cat])) + "\n\n"
        
        await message.edit(response.strip())
    except Exception as e:
        try:
            await message.edit(await localise(f"error: {str(e)}"))
        except:
            pass
