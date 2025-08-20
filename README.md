# channelBanlist# Telegram Ban-on-Leave Bot (Heroku-ready)

**Feature summary (Hindi):**
- `/start` par bot ek starting SMS bhejta hai.
- Bot ko channel/supergroup me **admin (ban permission)** banana hoga.
- Jo bhi member channel/supergroup **leave** karta hai, bot use **ban** kar dega (re-join rokne ke liye) aur **ban list** me add karega.
- `/banlist` se current chat ki ban list dekh sakte ho.
- `/ping` se health check.
- (Optional) `OWNER_ID` set ho to `/unban <user_id>` se unban kar sakte ho.

> **Note:** Heroku ka filesystem ephemeral hota hai — yeh repo bans ko `data/bans.json` me store karta hai jo dyno restart pe reset ho sakta hai. Production ke liye Heroku Postgres/Redis jaisa persistent storage use karen.

## Deploy on Heroku (Worker dyno with long polling)

1. **Create app** on Heroku.
2. **Config Vars** set karein:
   - `BOT_TOKEN` – aapke Telegram bot ka token (BotFather se).
   - `START_MESSAGE` – (optional) custom start SMS.
   - `OWNER_ID` – (optional) aapka Telegram user ID (unban command ke liye).
3. **Deploy** this repo to Heroku (GitHub connect ya manual push).
4. **Resources** tab me `worker` dyno ko **Enable** karein (web dyno ki zaroorat nahi).
5. Telegram me bot ko **channel/supergroup me add karke admin (ban power)** dein.

## Local run
```bash
BOT_TOKEN=123:ABC python bot.py
