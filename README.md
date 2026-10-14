# whatsapp-pdf-bot

Sends one Quran page every morning and one hadith every evening to a WhatsApp group, using GitHub Actions and Green API.

| What | When (Cairo time) | Source |
|---|---|---|
| Quran page (Madinah Mushaf image) | after 08:00 | quran.ksu.edu.sa |
| Hadith from Riyad as-Salihin (max 150 words) | after 20:00 | sunnah.com |

## How it works

- `.github/workflows/daily.yml` runs every 15 minutes.
- `dispatcher.py` checks the time and sends whatever is due. The date of each send is saved in `state.json`, so each message goes out **once per day at most**.
- `send_quran.py` / `send_hadith.py` do the actual sending.
- `state.json` holds the next Quran page, the next hadith number, and the last send dates.

## Settings

- **Time zone:** `BOT_TIMEZONE` in `daily.yml`
- **Send times:** `QURAN_TIME` / `HADITH_TIME` in `dispatcher.py`
- **Secrets** (repo Settings → Secrets → Actions): `GREEN_API_ID`, `GREEN_API_TOKEN`, `WHATSAPP_CHAT_ID`

## Send manually

Actions → **Daily Quran & Hadith** → Run workflow → choose `quran` or `hadith`.
To skip ahead or go back, edit `quran_page` / `hadith_index` in `state.json`.
