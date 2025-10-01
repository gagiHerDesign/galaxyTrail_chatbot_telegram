# Galaxy Trail Telegram Bot

#See the demo video here:
https://youtube.com/shorts/FmCyOCwAu6g?si=hcA2sMHGUwizCuCv

A Telegram bot for providing astronomy-related information (parks, sky events, light pollution, forecasts). Built with python-telegram-bot and designed to run as a long-running worker process (polling).

## Requirements
- Python 3.9+
- A virtual environment is recommended
- Dependencies listed in `requirements.txt`

## Environment variables
Copy `.env.sample` to `.env` for local testing and fill the values, or set the following secret env vars in your hosting provider (Render):

- `TOKEN` (Telegram bot token) (required)
- `NASA_API_KEY` (optional, if features use NASA APIs)
- `OPENWEATHER_KEY` (optional)
- `NEWS_API_KEY` (optional)

The project already raises an error if `TOKEN` is missing.

## Local setup
```bash
cd /path/to/galaxyTrail_chatbot_telegram
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env
# edit .env and add TOKEN and other keys
```

## Run locally
Use the virtualenv python to run the bot (preferred):

```bash
./venv/bin/python main.py
```

Or activate the venv then run:

```bash
source venv/bin/activate
python main.py
```

You should see console logs like "Starting bot..." and "Bot is running..." and polling messages.

## Deploying to Render
This repo includes a `Procfile` and `render.yaml` configured for a worker service.

Steps:
1. Push the repo to GitHub (or another git remote). See below for commands.
2. In Render, create a new service and connect the repository.
3. Choose "Worker" type. If Render doesn't detect `render.yaml`, set:
   - Build command: `pip install -r requirements.txt`
   - Start command: `python main.py`
4. Add the environment variables listed above in Render's dashboard (set `TOKEN` as a secret).
5. Deploy and watch logs for successful polling output.

## Push repo to GitHub (example commands)
If you already created a remote repo, run:

```bash
cd /path/to/galaxyTrail_chatbot_telegram
git remote add origin <REMOTE_URL>
git branch -M main
git push -u origin main
```

If you prefer to create the GitHub repo from your machine using GitHub CLI:

```bash
gh auth login
cd /path/to/galaxyTrail_chatbot_telegram
gh repo create your-username/repo-name --public --source=. --remote=origin --push
```

If your push is rejected due to large files (for example if `venv` was previously committed), clean the repo and force-push a fresh root commit (use carefully):

```bash
git checkout --orphan clean-main
git add -A
git commit -m "Initial commit (clean)"
git push -u origin clean-main:main --force
```

## Notes & Tips
- Do not commit `.env` or your bot token. Use Render / GitHub secrets for production.
- The bot currently uses polling; switching to webhooks requires a web endpoint and a public HTTPS URL.

## Troubleshooting
- Exit code 127 when running `python main.py` usually means wrong Python path or missing dependencies. Activate the virtualenv and use `./venv/bin/python main.py`.

---

If you want edits (more details, screenshots, or a webhook deployment section + Dockerfile), tell me which section to expand.
