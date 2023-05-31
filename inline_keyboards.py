from aiogram.types import  InlineKeyboardButton, InlineKeyboardMarkup
from sqlite import get_projects_name_for_user
from upload_google_drive import get_list_of_current_project_files


ikb_file = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton('Надо загрузить файл', callback_data='with_file')],[InlineKeyboardButton('Файл загружать не нужно', callback_data='without_file')]])
ikb_cancel = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton('Вернуться в стартовое меню', callback_data='cancel')]])


def get_inline_keybord_for_edit(user_id):
    edit_ikeyboard = InlineKeyboardMarkup(row_width=1)
    for group in get_projects_name_for_user(user_id):
        btn_text = group[0]
        btn_callback = group[0]
        edit_ikeyboard.add(InlineKeyboardButton(text=btn_text, callback_data=btn_callback))
    return edit_ikeyboard

ikb_done_or_not = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton('Да', callback_data='yes')],[InlineKeyboardButton('Нет', callback_data='no')]])


ikb_edit_menu = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton('Описание', callback_data='edit_description'),
                                                      InlineKeyboardButton('Дата уведомления', callback_data='edit_notice_date'),
                                                       InlineKeyboardButton('Периодическое/не переодическое', callback_data='edit_periodic')],
                                                      [InlineKeyboardButton('Файлы', callback_data='edit_files'),
                                                       InlineKeyboardButton('Состояние', callback_data='edit_state'),
                                                       InlineKeyboardButton('Время уведомления', callback_data='edit_time')]])

ikb_files = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton('Загрузить ещё', callback_data='add_more_files'),
                                                   InlineKeyboardButton('Я уже все загрузил(а)', callback_data='end_add_files')]])


ikb_add_delete_files = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton('Удалить файлы',callback_data='delete_files')],[InlineKeyboardButton('Добавить файлы', callback_data='upload_new_files')]])

ikb_after_delete = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton('Удалить ещё файлы', callback_data='delete_more_files')], [InlineKeyboardButton('Закончить удаление',
                                                                                                                                                               callback_data='end_deleting_files')]])


def get_files_from_disk(user_id, project_name):
    del_file_ikeyboard = InlineKeyboardMarkup(row_width=1)
    for file in get_list_of_current_project_files(user_id, project_name):
        btn_text = file['title']
        btn_callback = file['id']
        del_file_ikeyboard.add(InlineKeyboardButton(text=btn_text, callback_data=btn_callback))
    return del_file_ikeyboard
