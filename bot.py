import vk_api
import requests
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
import uuid

main_token = "ec9e34640d279ade058cf06d0d0f89713a9e23392ab6d590bed712493903aa197888add07056c71a86faf"
vk_session = vk_api.VkApi(token=main_token)
longpoll = VkBotLongPoll(vk_session, 195307807)


def sender_chat(chat_id, text):
    vk_session.method('messages.send', {'chat_id': chat_id, 'message': text, 'random_id': get_random_id()})


def download_image_in_message_and_save_image_name(object_message):
    url_img = object_message.get('attachments')[0].get('photo').get('sizes')[-1].get('url')
    r = requests.get(url_img)

    name_file_img = uuid.uuid4().hex
    with open(f'media/photo/{name_file_img}.jpg', 'wb') as f:
        f.write(r.content)

    return name_file_img


for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat:

        id_chat = event.chat_id
        msg_object = event.object.message
        msg_text = msg_object['text'].lower()
        split_message = msg_text.split(' ')

        if msg_object.get('attachments'):

            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            tessdata_dir_config = r'C:\Program Files (x86)\Tesseract-OCR\tessdata'
            from PIL import Image

            if msg_object.get('attachments')[0].get('type') == 'photo' and msg_text == '123':
                img_name = download_image_in_message_and_save_image_name(msg_object)

                image = Image.open(f"media/photo/{img_name}.jpg")
                text_in_image = pytesseract.image_to_string(image, lang='rus', config=tessdata_dir_config)
                sender_chat(id_chat, f'Текст с картинки - {text_in_image}')

        # status
        if msg_text == "status":
            sender_chat(id_chat, "Ok!")

        # wiki
        import wikipedia

        wikipedia.set_lang("RU")
        wiki_word = ['wiki', 'wikipedia', 'вики', 'википедия']

        if split_message[0] in wiki_word:
            msg_for_wiki = " ".join(split_message[1:])
            try:
                sender_chat(id_chat, str(wikipedia.summary(msg_for_wiki)))
            except wikipedia.exceptions.DisambiguationError as e:
                sender_chat(id_chat, str(e.options))
                sender_chat(id_chat, "Данный вариант имеет много статей, попробуйте написать по другому")
            except wikipedia.exceptions.PageError:
                sender_chat(id_chat, "Такой страницы не существует")

        # translate
        import translators as ts

        translator_word = ['переведи', 'перевод', 'translate']
        key_from_lang = {
            'русский': 'ru',
            'английский': 'en',
            'немецкий': 'de',
            'китайский': 'zh',
            'французский': 'fr',
            'испанский': 'es',
            'итальянский': 'it',
        }
        to_language = 'ru'

        if split_message[0] in translator_word:
            if split_message[-2] in '***':
                try:
                    to_language = key_from_lang[split_message[-1]].lower()
                except KeyError:
                    sender_chat(id_chat, f'В словаре нет языка {split_message[-1]}, либо такого языка не существует.'
                                         f'Будет переведено на автоматический язык (русский)')
                split_message[:] = split_message[0:-2]
            msg_for_translator = ' '.join(split_message[1:])
            sender_chat(id_chat, str(ts.google(msg_for_translator, from_language='auto', to_language=to_language)))
