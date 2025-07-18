# Telegram Link Extractor

A Python tool to automatically extract group and channel invite links from your Telegram chats.  

---

## 🚀 Features

- Connects directly to your Telegram account
- Scans all your account chats (dialogs)
- Detects and extracts group / channel / supergroup invitation links
- Retrieves title and type of each link
- Supports filtering by date to limit the search
- Generates a clean CSV report
- Console output with real-time progress

---

## 📍Installation & Usage


```bash
git clone https://github.com/amirfabo/telegram-link-extractor.git
cd telegram-link-extractor
```

**You need install requirements before use:**

Python 3.10+

```bash
pip install Telethon
```

### ⚙️ Configure your settings:

- Edit the included **settings.json** file.

- Add your `api_id` and `api_hash` from my.telegram.org.

- Set `offset_date` if you want to scan only messages previous a specific date (format: ```YYYY-MM-DD```).

- Specify the CSV output path.

```json
{
  "auth": {
    "api_id": "YOUR_API_ID",
    "api_hash": "YOUR_API_HASH"
  },
  "general": {
    "offset_date": "2024-01-01" // or null
  },
  "output": {
    "path": "output.csv"
  }
}
```

**Then you can run scanner with this command:**

```bash
python3 main.py
```

### 📄 Output

The result CSV file will include these columns:

- `URL` : The invitation link of channel or group 
- `Type` : `CHANNEL`/`CHAT`/`MEGAGROUP`/`BOT`/`USER`
- `Title` : The title of the group or channel (if available)

## 📞 Contact

If you have any questions, suggestions, or need support, feel free to reach out:

- Email: [amirfabo@yahoo.com](mailto:amirfabo@yahoo.com)
- Telegram: [@ItsFaBo](https://t.me/ItsFaBo)
- GitHub Issues: [Open an issue](https://github.com/YourUsername/telegram-link-extractor/issues)

We’d love to hear from you!