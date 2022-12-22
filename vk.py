import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
import random
import argparse
import re

from magic_dict import MagicDict
from text_generator import TextGenerator

parser = argparse.ArgumentParser(description="Генератор текста на основе цепей Маркова")
# parser.add_argument("dir", type=str, help="Путь к файлу с текстом или модели, если установлен параметр load-model")
parser.add_argument("--save-dir", type=str, help="Путь для сохранения модели")
parser.add_argument("--load-model", type=bool, help="Если True, загружает заданную модель")
parser.add_argument("--length", type=int, help="Длинна генерируемого текста", default=5)
parser.add_argument("--encoding", type=str, help="Кодировка файла", default="utf-8")
args = parser.parse_args()

counter = 1

def smswr(senders, message):  # отправить сообщение в лс
    vks.method('messages.send', {'chat_id': senders, 'message': message, 'random_id': get_random_id()})


vks = vk_api.VkApi(token='')
vk = vks.get_api()
longpoll = VkBotLongPoll(vks, group_id=201564429) # 194906739

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW and event.from_user and event.message.get("text") != "":
        text = event.message.get("text")
        sender = event.message.get("from_id")
        if text.startswith('/удалить'):
            with open('memory.txt', 'r', encoding="utf-8") as f:
                old_data = f.read()
            new_data = old_data.replace(text[9:], '')
            with open('memory.txt', 'w', encoding="utf-8") as f:
                f.write(new_data)
            f.close()
            print(text[9:])
            vks.method('messages.send', {'user_id': sender, 'message': 'Строчка удалена', 'random_id': get_random_id()})
    if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat and event.message.get("text") != "":
        sender = event.chat_id
        text = event.message.get("text")
        if counter != 10:
            text = text.split(' ')
            print('Счётчик:', counter)
            for element in text:
                element = re.sub(r'[^\w\s]', '', element)
                fr = open('memory.txt', 'r', encoding="utf-8")
                lines = fr.readlines()
                if len(element) < 9:
                    f = open('memory.txt', "a", encoding="utf-8")
                    f.write(element + "\n")
                    f.close()
                else:
                    element = element.encode('utf-8')
                    print(f'Фильтр: {element}')
            counter += 1
        else:
            counter = 1
            with open('memory.txt', "r", encoding="utf-8") as file:
                text = file.read()
            base_text = MagicDict(text)
            base_model = base_text.generate()
            generated_text = TextGenerator(base_model, random.randint(1, 7)).create_text()
            smswr(event.chat_id, generated_text.encode('utf-8'))
