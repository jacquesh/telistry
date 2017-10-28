# Telistry

Telegram currently doesn't give you any [reasonable](https://telegram.wiki/general/pdfexport) way to get a local copy of your entire chat history, so Telistry will do it for you instead.

Using it is simple:
```python
from telistry import run

if __name__ == '__main__':
    api_id = '<your_api_id_here>'
    api_hash = '<your_api_hash_here>'
    phone_number = '<your_telegram_account_phone_number_here>'
    run(api_id, api_hash, phone_number)
```

You can get your telegram API credentials at [my.telegram.org](https://my.telegram.org/apps)
