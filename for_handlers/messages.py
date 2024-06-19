from string import punctuation

from aiogram.types import Message

restricted_words = {'хуй', 'сука', 'даун', 'имбицил', 'дурак', 'ебало', 'пизда', 'fuck', 'trash', 'shit', 'пиздец',
                    'пиздарас', 'уебок', 'хуйло', 'пиздализ', 'хуесос', 'конченный', 'retard', 'ебал',
                    'хуйня', 'лох', 'говнюк', 'жопа', 'лошара', 'нахуй', 'пизду'}


# # защита от символов между плохими словами
def clean_text(text: str):
    return text.translate(str.maketrans('', '', punctuation))


# # защита от плохих слов, также бан этого юзера (в комменте)

async def get_shop_message(message: Message) -> str:
    if restricted_words.intersection(clean_text(message.text.lower()).split()):
        return (
            "Не ругайтесь пожалуйста 😊"
        )
    else:
        return (
            "Весь функционал доступен в нашем интернет-магазине.\n"
            'Нажмите "Открыть магазин", чтобы приступить к покупкам'
        )
