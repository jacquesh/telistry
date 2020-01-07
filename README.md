# Telistry

Telegram currently doesn't give you any [reasonable](https://telegram.wiki/general/pdfexport) way to get a local copy of your entire chat history.
Telistry is a Python script (requires Python 3.8 or later) that will download the entire history of all of your open chats to local text files. Images and other files that were sent in those chats will also be downloaded.

Using in your own program it is simple:
```python
from telistry import run

if __name__ == '__main__':
    api_id = '<your_api_id_here>'
    api_hash = '<your_api_hash_here>'
    phone_number = '<your_telegram_account_phone_number_here>'
    run(api_id, api_hash, phone_number)
```

or you can run it from the command line
```
$ python3 telistry.py <your_api_id_here> <your_api_hash_here> <your_telegram_account_phone_number_here>
```

You can get your telegram API credentials at [my.telegram.org](https://my.telegram.org/apps)
