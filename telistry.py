import os.path

from telethon import TelegramClient
from telethon.tl.types import (
    Chat, User,
    MessageMediaPhoto, MessageMediaDocument,
    DocumentAttributeFilename,
    PeerUser, PeerChat
)

log_root = 'log'
media_root = 'media'
media_tmp = os.path.join(media_root, 'tmp')

def get_user_name(user):
    first_name = ''
    last_name = ''
    if user.first_name is not None:
        first_name = user.first_name
    if user.last_name is not None:
        last_name = user.last_name
    return first_name+' '+last_name

def get_entity_last_msg(tmp_user):
    entity_dir = os.path.join(log_root, tmp_user['name'])
    if not os.path.isdir(entity_dir):
        return 0

    log_file_name = os.path.join(entity_dir, 'log.txt')
    if not os.path.isfile(log_file_name):
        return 0

    with open(log_file_name, 'r', encoding='utf-8') as log_file:
        log_contents = log_file.read()

    line_end_index = len(log_contents)
    last_newline = line_end_index
    while last_newline >= 0:
        line_tokens = log_contents[last_newline+1:line_end_index].split(' ')
        if len(line_tokens) > 0:
            id_token = line_tokens[0]
            if id_token.isdigit():
                return int(id_token)

        line_end_index = last_newline
        last_newline = log_contents.rfind('\n', 0, line_end_index)
    return 0

def get_all_pseudousers(client, entities):
    users = {}
    me = client.get_me()
    for e in entities+[me]:
        tmp_user = {}
        if isinstance(e, User):
            tmp_user['name'] = get_user_name(e).strip()
            tmp_user['peer'] = PeerUser(e.id)
        elif isinstance(e, Chat):
            tmp_user['name'] = e.title.strip()
            tmp_user['peer'] = PeerChat(e.id)

        tmp_user['id'] = e.id
        tmp_user['last_msg_id'] = get_entity_last_msg(tmp_user)
        users[e.id] = tmp_user
    return users

def message_media_exists(msg):
    msg_id = str(msg.id)
    for entry in os.listdir(media_root):
        if entry.startswith(msg_id):
            return True
    return False

def download_message_media(client, msg):
    os.makedirs(media_tmp, exist_ok=True)
    if message_media_exists(msg):
        return

    download_destination = media_tmp
    if isinstance(msg.media, MessageMediaPhoto):
        download_destination = os.path.join(media_tmp, 'tmp.jpg')
    elif isinstance(msg.media, MessageMediaDocument):
        for attrib in msg.media.document.attributes:
            if isinstance(attrib, DocumentAttributeFilename):
                attrib_name, attrib_ext = os.path.splitext(attrib.file_name)
                download_destination = os.path.join(media_tmp, 'temp'+attrib_ext)


    tmp_filename = client.download_media(msg.media, file=download_destination)
    if tmp_filename is None:
        return
    _, extension = os.path.splitext(tmp_filename)
    media_name = '%d%s' % (msg.id, extension)
    media_path = os.path.join(media_root, media_name)
    os.rename(tmp_filename, media_path)

def get_history(client, pseudouser):
    last_msg_id = 0
    messages = []
    while True:
        _,tmp_messages,_ = client.get_message_history(pseudouser['peer'],
                                                      limit=4096,
                                                      offset_id=last_msg_id,
                                                      min_id=pseudouser['last_msg_id'])
        if len(tmp_messages) == 0:
            break
        last_msg_id = tmp_messages[-1].id
        messages += tmp_messages
    return messages

def write_history(client, all_users, user, messages):
    user_dir = os.path.join(log_root, user['name'])
    os.makedirs(user_dir, exist_ok=True)

    file_path = os.path.join(user_dir, 'log.txt')
    header_needed = not os.path.isfile(file_path)
    outfile = open(file_path, 'a', encoding='utf-8')
    if header_needed:
        outfile.write('%d: %s\n' % (user['id'], user['name']))
    for msg in reversed(messages):
        # Useful fields: msg.id, msg.date, msg.from_id
        if getattr(msg, 'media', None):
            download_message_media(client, msg)
            media_type = type(msg.media).__name__
            media_caption = getattr(msg.media, 'caption', '')
            content = '[%s] %s' % (media_type, media_caption)
        elif hasattr(msg, 'action'):
            # TODO: Print a prettier message for the action
            content = 'Action:\n' + msg.action.stringify()
        else:
            content = ''

        if hasattr(msg, 'message'):
            content += msg.message

        username = 'UNKNOWNUSER'
        if msg.from_id in all_users:
            username = all_users[msg.from_id]['name']

        outfile.write('%d @ %s: <%s> %s\n' % (msg.id, str(msg.date), username, content))
    outfile.close()

def run(api_id, api_hash, phone_number):
    session_id = 'chat_downloader_session'
    client = TelegramClient(session_id, api_id=api_id, api_hash=api_hash)

    print("Connecting to the Telegram service...")
    client.connect()
    if not client.is_user_authorized():
        client.send_code_request(phone_number)
        auth_code = input('Enter the authentication code you received:')
        client.sign_in(phone_number, auth_code)

    print("Collecting open chat diaglogs...")
    dialogs, entities = client.get_dialogs()
    users = get_all_pseudousers(client, entities)

    for uid, user in users.items():
        print('Downloading history for %s...' % user['name'])
        messages = get_history(client, user)
        write_history(client, users, user, messages)

if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser(description='Download your telegram chat history reasonably')
  parser.add_argument('api_id', help='The API for your app')
  parser.add_argument('api_hash', help='The API secret hash')
  parser.add_argument('phone_number', help='The phone number of the account')
  args = parser.parse_args()
  run(args.api_id,args.api_hash,args.phone_number)
