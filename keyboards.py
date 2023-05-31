from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


kb_start = ReplyKeyboardMarkup(resize_keyboard=True)
b1 = KeyboardButton('Запланировать дело')
b2 = KeyboardButton('Текущие дела')
b3 = KeyboardButton('Выполненные дела')
b4 = KeyboardButton('/start')
kb_start.add(b1).insert(b2).add(b3).insert(b4)



