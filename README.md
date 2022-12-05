# Simple Python TG Ping Bot
- Determines whether host is reachable via ping (os.system).
- Results are posted in Telegram channel if current check result differs from last one.
- config_sample.ini should be renamed into config.ini and fullfilled with needed values.
- Adding downtime/uptime to response text is configured in post_status_update() function

# Dependencies
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) (20.0a1+ version)
