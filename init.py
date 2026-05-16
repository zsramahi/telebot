from pyrogram import Client, filters, idle
from pathlib import Path
import importlib.util
import config
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from googletrans import Translator

translator = Translator()

async def localise(msg):
    lang = getattr(config, "language", "en")
    if lang == "en":
        return msg
    try:
        result = await translator.translate(msg, dest=lang)
        return result.text
    except:
        return msg

app = Client(
    "account",
    api_id=config.apiid,
    api_hash=config.apihash
)

modules = {}
modulecount = 0
afkenabled = False
categoryorder = ["general", "games", "crypto", "settings"]

class ModuleReloader(FileSystemEventHandler):
    def __init__(self, loop):
        self.loop = loop
        self.debounce = {}
    
    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.py'):
            asyncio.run_coroutine_threadsafe(self.reload(), self.loop)
    
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.py'):
            asyncio.run_coroutine_threadsafe(self.reload(), self.loop)
    
    def on_deleted(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.py'):
            asyncio.run_coroutine_threadsafe(self.reload(), self.loop)
    
    async def reload(self):
        await asyncio.sleep(0.5)
        load()
        print(f"reloaded {modulecount} modules")

def load():
    global modulecount
    modules.clear()
    moduledir = Path("modules")
    modulecount = 0
    for file in moduledir.glob("*.py"):
        if file.name.startswith("_"):
            continue
            
        spec = importlib.util.spec_from_file_location(file.stem, file)
        module = importlib.util.module_from_spec(spec)
        module.localise = localise
        spec.loader.exec_module(module)
        
        if hasattr(module, "name") and hasattr(module, "execute"):
            modules[module.name] = module
            modulecount += 1
            if hasattr(module, "aliases"):
                for alias in module.aliases:
                    modules[alias] = module

@app.on_message(filters.me & filters.text)
async def handle(client, message):
    try:
        text = message.text
        prefix = getattr(config, "prefix", ".")
        if not text.startswith(prefix):
            return
        
        command = text[len(prefix):].split()[0]
        
        if command in modules:
            if getattr(config, "autodelete", False):
                asyncio.create_task(autodelete(message))
            await modules[command].execute(client, message)
    except Exception as e:
        try:
            await message.edit(await localise(f"error: {str(e)}"))
        except:
            pass

async def autodelete(message):
    await asyncio.sleep(60)
    try:
        await message.delete()
    except:
        pass

@app.on_message(filters.private & filters.incoming & ~filters.me)
async def afkhandle(client, message):
    try:
        if afkenabled:
            if hasattr(config, "afkmessage"):
                await message.reply(config.afkmessage)
            else:
                await message.reply("hey there, im currently away from my device and will be back soon to help you.")
    except:
        pass

async def start():
    await app.start()
    load()
    me = await app.get_me()
    print(f"logged in as {me.first_name} (@{me.username})")
    print(f"loaded {modulecount} modules")
    
    loop = asyncio.get_event_loop()
    handler = ModuleReloader(loop)
    observer = Observer()
    observer.schedule(handler, "modules", recursive=False)
    observer.start()
    print("hot reload enabled")
    
    await idle()
    
    observer.stop()
    observer.join()
    await app.stop()

if __name__ == "__main__":
    app.run(start())
