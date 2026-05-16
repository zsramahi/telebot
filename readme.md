# telebot

a lightweight telegram selfbot built on pyrogram. runs on your own
account, listens for messages you send that start with a configurable
prefix, and dispatches to one of 24 commands.

## features

- 24 modular commands across general, games, crypto, settings
- hot reload of modules without restarting
- multilingual output via on-the-fly translation
- flat python config file, no database
- streaming ai chat via openrouter
- on-chain trace for btc, eth, ltc, trx, xrp, sol

## requirements

- python 3.9+
- a telegram account
- api credentials from https://my.telegram.org
- optional: openrouter api key for the chat command

## setup

1. clone the repo
   ```
   git clone https://github.com/zsramahi/telebot.git
   cd telebot
   ```

2. install dependencies
   ```
   pip install -r requirements.txt
   pip install wikipedia
   ```

3. fill in `config.py`
   ```python
   apiid = 12345
   apihash = "your-api-hash"
   openrouterapikey = "your-key"
   ```

4. run
   ```
   python init.py
   ```

   on first launch pyrogram asks for your phone number, login code,
   and 2fa password if set. an `account.session` file is created.
   keep it safe.

## usage

every command starts with the prefix (default `.`). change it with
`.prefix !`.

### general
- `.afk` / `.afk "message"` / `.afk reset`
- `.chat "query"` (aliases `.ai`, `.ask`; append ` --stream`)
- `.gc` create a new groupchat
- `.log [n]` save chat history to a file
- `.ping` round-trip latency
- `.purge [n]` delete messages (alias `.delete`)
- `.search "query"` wikipedia (alias `.wiki`)
- `.spam "text" 50` / `.spam stop`
- `.tts "text"` text to speech (aliases `.t2s`, `.texttospeech`)
- `.translate "text"` or reply to a message
- `.whois @username` user info (alias `.info`)
- `.price btc` crypto/metals price

### games
- `.dice` roll a die
- `.bb` shoot a basketball (alias `.basketball`)

### crypto
- `.btc [address]` show or set bitcoin address (alias `.bitcoin`)
- `.eth [address]` ethereum (alias `.ethereum`)
- `.ltc [address]` litecoin (alias `.litecoin`)
- `.sol [address]` solana (alias `.solana`)
- `.trace [address or txid]` on-chain trace (alias `.check`)

### settings
- `.autodelete` toggle 60s auto-delete of command messages
- `.help` list all commands (aliases `.cmds`, `.cmd`)
- `.language [name]` switch translation language
- `.prefix [char]` change the command prefix

## notes

- selfbots are against telegram's tos. use at your own risk.
- changes to files in `modules/` are picked up live, no restart.
- settings persist by rewriting `config.py` itself.
