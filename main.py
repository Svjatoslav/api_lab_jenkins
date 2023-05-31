import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from inline_keyboards import ikb_file, ikb_cancel, get_inline_keybord_for_edit, ikb_edit_menu,ikb_files,ikb_add_delete_files, get_files_from_disk
from config import BOT_TOKEN
from keyboards import kb_start
from aiogram_calendar import simple_cal_callback, SimpleCalendar
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from sqlite import create_project, db_start, edit_project, get_state_of_task, edit_state_of_task, get_done_tasks, \
    get_not_done_tasks,edit_task_description, delete_my_task,edit_task_time, get_awaiting_tasks, replace_await_by_send, select_date_task_for_periodic,\
    update_date_task_for_pereodic, get_periodic_state, update_pereodic_of_task_yes,update_pereodic_of_task_no, get_users
from upload_google_drive import another_way, upload_file_on_drive, delete_files_from_google_disk
from scripts import check_for_notification, add_days
import aioschedule





async def on_startup(_):
    await db_start()
    asyncio.create_task(scheduler())


Storage = MemoryStorage()
bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot, storage=Storage)

START_TEXT = """
<b>Доступные команды, помимо тех, что на кнопках.</b> 
<b>/edit_my_task</b> -<strong>изменить задание</strong>
<b>/delete</b> - <strong>удалить дело</strong>
<b>/exit</b> - <strong>выход в главное меню</strong>
"""
class DeleteTasks(StatesGroup):
    Delete_task = State()

class EditTasks(StatesGroup):
    Get_inline_menu = State()
    Edit_Calendar = State()
    Edit_Description = State()
    Edit_Time = State()
    Edit_Periodic = State()
    Edit_Files = State()
    Delete_Files = State()

class PlanThingsProcces(StatesGroup):
    Calendar = State()
    Description = State()
    FileName = State()
    Document = State()
    NotificationTime = State()


#команда старт
@dp.message_handler(commands=['start'],state="*")
async def start(message: types.Message,state:FSMContext):
    await bot.send_message(chat_id = message.from_user.id,
                           text = START_TEXT,
                           parse_mode = 'HTML',
                           reply_markup = kb_start)
    await state.finish()


#запускает функцию notification_function каждую минуту (расписание).
async def scheduler():
    aioschedule.every(1).minutes.do(notification_function)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)



#реализация кнопки "текущие дела"
@dp.message_handler(text=['Текущие дела'])
async def current_tasks(message:types.Message):
    done_tasks = ""
    #выгружаем из базы данных все дела, находящиеся в списке "текущих" т.е в колонке done_or_not стоит 0
    tasks = get_done_tasks(message.from_user.id)

    num = 1
    for task in tasks:
        done_tasks += f"<b>{num}.{task[3]}</b>- {task[4]}- <b>{task[1]}</b>\n {task[2]}\n"
        num = num + 1
    await bot.send_message(message.chat.id, '<b>Ваши текущие дела:</b>\n\n' + done_tasks,
                           parse_mode=types.ParseMode.HTML)

#реализация кнопки "выполненные дела"
@dp.message_handler(text=['Выполненные дела'])
async def current_tasks(message:types.Message):
    not_done_tasks = ""
    # выгружаем из базы данных все дела, находящиеся в списке "выполненных" т.е в колонке done_or_not стоит 1
    tasks = get_not_done_tasks(message.from_user.id)
    print(tasks)
    num = 1
    for task in tasks:
        not_done_tasks += f"<b>{num}. {task[3]}</b> - <b>{task[1]}</b>\n {task[2]}\n"
        num = num + 1
    await bot.send_message(message.chat.id, '<b>Ваши выполненные дела:</b>\n\n' + not_done_tasks,
                           parse_mode=types.ParseMode.HTML)


#удаление проекта (задания)
@dp.message_handler(commands=['delete'])
async def delete_tasks_by_name(message: Message):
    await bot.send_message(chat_id=message.from_user.id,
                       text='Выберите проект, который хотите удалить',
                       reply_markup=get_inline_keybord_for_edit(message.from_user.id))
    await DeleteTasks.Delete_task.set()


#удаление проекта (задания)
@dp.callback_query_handler(state=DeleteTasks.Delete_task)
async def del_current_task(callbak:CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        data['name'] = callbak.data
    #удаляем проект по id пользователя и имени проекта (эта пара записей является ключем)
    await delete_my_task(state,callbak.from_user.id)
    await bot.send_message(chat_id=callbak.from_user.id, text = 'Задание успешно удалено!')
    await state.finish()



#сбрасывает состояние
@dp.message_handler(commands=['exit'], state = EditTasks.Get_inline_menu)
async def exit_to_menu(message: Message, state: FSMContext)->None:
    await message.answer(text='Вы в главном меню')
    await state.finish()


#запланировать дело
@dp.message_handler(text=['Запланировать дело'])
async def plan_some_things(message: types.Message, state: FSMContext)->None:
    await bot.send_message(chat_id = message.from_user.id,
                           text = 'Придумайте название для своего проекта)')
    await PlanThingsProcces.Description.set()


#описание для создаваемого проекта
@dp.message_handler(state = PlanThingsProcces.Description)
async def make_some_description(message: types.Message,state: FSMContext)->None:
    async with state.proxy() as data_dict:
        data_dict['project_name'] = message.text,
        #создание папки на гугл диске папки с названием - {user_id} и вложенной в неё папки {название текущего проекта}
        another_way(str(message.from_user.id), message.text)
    await bot.send_message(chat_id=message.from_user.id,
                           text = 'Введите описание')
    await PlanThingsProcces.Calendar.set()




#календарь
@dp.message_handler(state=PlanThingsProcces.Calendar)
async def call_calendar(message: Message, state: FSMContext):
    async with state.proxy() as data_dict:
        data_dict['description'] = message.text,
    await message.answer("Please select a date: ", reply_markup=await SimpleCalendar().start_calendar())

#обработка календаря
@dp.callback_query_handler(simple_cal_callback.filter(), state = PlanThingsProcces.Calendar)
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict,state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    async with state.proxy() as data_dict:
        data_dict['project_date'] = date.strftime("%d/%m/%Y")
    if selected:
        await callback_query.message.answer(
            f'You selected {date.strftime("%d/%m/%Y")}',
            reply_markup=ikb_file
        )

#Первая ступень "редактирования записей"
@dp.message_handler(commands=['edit_my_task'])
async def edit_projects(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text='Выберите проект, который хотите редактировать',
                           #выводится список проектов, доступных данному юзеру для редактирования в виде Inline клавиатуры
                           reply_markup=get_inline_keybord_for_edit(message.from_user.id))
    await EditTasks.Get_inline_menu.set()

#функция позволяет выбрать какой элемент проекта редактировать
@dp.callback_query_handler(text='edit_files',state=EditTasks.Get_inline_menu)
async def edit_files_for_tasks(callback: CallbackQuery):
    await bot.send_message(chat_id=callback.from_user.id,
                           text='Выберите, что вы хотите сделать',
                           reply_markup=ikb_add_delete_files)


#функция позволяет удалить файл из конкретного проекта с гугл диска.
@dp.callback_query_handler(text='delete_files', state=EditTasks.Get_inline_menu)
async def choose_file_for_deleting(callback:CallbackQuery,state:FSMContext):
    async with state.proxy() as data:
        await bot.send_message(chat_id=callback.from_user.id, text='Выберите файл для удаления',reply_markup=get_files_from_disk(callback.from_user.id,data['name']))
    await EditTasks.Delete_Files.set()


#обработчик удаления
@dp.callback_query_handler(state = EditTasks.Delete_Files)
async def delete_files_from_disk(callback:CallbackQuery, state:FSMContext):
    #удаляет файл с диска по его id, id получаем из inline keyboard (с момента, когда выбирали какой проект будет редактировать)
    delete_files_from_google_disk(callback['data'])
    await bot.send_message(chat_id=callback.from_user.id, text = 'Файл успено удалён!')
    await state.finish()


#позволяет загрузить файл на гугл диск в папку текущего проекта (вводить имя с расширением)
@dp.callback_query_handler(text='upload_new_files',state=EditTasks.Get_inline_menu)
async def upload_files(callback:CallbackQuery):
    await bot.send_message(chat_id=callback.from_user.id,text='Введите желаемое название файла.В формате <strong>FileName</strong>.формат(txt,xlsx,...) ',parse_mode='HTML')
    await EditTasks.Edit_Files.set()

#загрузка нового файла на гугл диск
@dp.message_handler(state=EditTasks.Edit_Files)
async def uplode_new_files(message:Message, state: FSMContext):
    await bot.send_message(chat_id=message.from_user.id,
                           text='Загрузи файл',
                           reply_markup=ikb_cancel)
    async with state.proxy() as data:
        data['file_name'] = message.text


#обработчик загрузки файла и upload его на гугл диск
@dp.message_handler(content_types = types.ContentTypes.DOCUMENT, state = EditTasks.Edit_Files)
async def doc_handler(message: types.Message, state: FSMContext)-> None:
    async with state.proxy() as data:
        if document := message.document:
            await document.download(
                destination_file=f"{data['file_name']}",
            )
        #создает файл filename в нужной директории на гугл диске
        upload_file_on_drive(str(message.from_user.id), data['name'], data['file_name'])
    await bot.send_message(chat_id=message.from_user.id,
                           text='Успешно! Файл загружен)'
                        )
    await state.finish()





#изменение описания
@dp.callback_query_handler(text='edit_description', state=EditTasks.Get_inline_menu)
async def edit_description(callback: CallbackQuery):
    await callback.message.answer('Введите новое описание')
    await EditTasks.Edit_Description.set()

#изменение времени
@dp.callback_query_handler(text='edit_time', state=EditTasks.Get_inline_menu)
async def edit_description(callback: CallbackQuery):
    await callback.message.answer('Введите новое время')
    await EditTasks.Edit_Time.set()


"""перевод задачи в класс периодических. Т.е после отправки уведомления, 
в графу статус не установится значение "send" а вместо этого, дата уведомления увеличится на период (в днях), указанный пользователем"""

@dp.callback_query_handler(text='edit_periodic',state=EditTasks.Get_inline_menu)
async def edit_periodic_state(callback:CallbackQuery, state:FSMContext):
    period = await get_periodic_state(state,callback.from_user.id)
    print(period)
    if period[0] == 0:
        await bot.send_message(chat_id=callback.from_user.id, text='Введите желаемый период в днях')
        await EditTasks.Edit_Periodic.set()
    else:
        await update_pereodic_of_task_no(callback.from_user.id, state)
        await bot.send_message(chat_id=callback.from_user.id, text = 'Успешно! Задание теперь не периодическое')
        await state.finish()

#обработка ввода периода пользователем
@dp.message_handler(state=EditTasks.Edit_Periodic)
async def set_period(message:Message,state:FSMContext):
    await update_pereodic_of_task_yes(message.from_user.id,state,int(message.text))
    await message.answer(f'Успешно! Период задания = {message.text}')
    await state.finish()



#обработка изменения времени
@dp.message_handler(state=EditTasks.Edit_Time)
async def set_new_description(message: Message,state:FSMContext):
    async with state.proxy() as data:
        data['notification_time'] = message.text
    #меняем время уведомления в базе данных
    await edit_task_time(state, message.from_user.id)
    await bot.send_message(chat_id=message.from_user.id,
                           text='Время успешно изменено')
    await EditTasks.Get_inline_menu.set()


#обработка изменения описания
@dp.message_handler(state=EditTasks.Edit_Description)
async def set_new_description(message: Message,state:FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    #изменения поля description в базе данных
    await edit_task_description(state, message.from_user.id)
    await bot.send_message(chat_id=message.from_user.id,
                           text='Описание успешно изменено')
    await EditTasks.Get_inline_menu.set()

#изменение даты уведомления
@dp.callback_query_handler(text = 'edit_notice_date', state=EditTasks.Get_inline_menu)
async def edit_done_or_not(callback: CallbackQuery):
    await callback.message.answer("Please select a date: ", reply_markup=await SimpleCalendar().start_calendar())
    await EditTasks.Edit_Calendar.set()

"""изменение состояния дела с текущее -> выполненное, в графе done_or_not ставим еденицу и сносим время и дату
                              выполненное -> текущее, дается возможность установить дату и время
"""
@dp.callback_query_handler(text='edit_state', state=EditTasks.Get_inline_menu)
async def edit_done_station(callback: CallbackQuery,state: FSMContext)->None:
    done = await get_state_of_task(state, callback.from_user.id)
    done = int(done)
    if done == 0:
        flag = 1
        await bot.send_message(chat_id=callback.from_user.id,
                               text = 'Успешно! Дело помечено как выполненное.')
        await edit_state_of_task(state, callback.from_user.id, flag)
    else:
        await bot.send_message(chat_id=callback.from_user.id,
                               text='Успешно! Дело возвращено в список текущих. Не заново установить дату и время для уведомления)')
        flag = 0
        await edit_state_of_task(state, callback.from_user.id,flag)
    await EditTasks.Get_inline_menu.set()


#выбор параметра, который хотим изменить
@dp.callback_query_handler(state=EditTasks.Get_inline_menu)
async def get_edit_inline_keyboard(callback: CallbackQuery, state: FSMContext)->None:
    async with state.proxy() as data:
        data['name'] = callback['data']
    await bot.send_message(chat_id=callback.from_user.id, text = 'Выберите, что хотите отредактировать. Для завершения измениней, напишите /exit',
                           reply_markup=ikb_edit_menu)


#изменение даты проекта
@dp.callback_query_handler(simple_cal_callback.filter(), state = EditTasks.Edit_Calendar)
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict,state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    async with state.proxy() as data:
        data['date'] = date.strftime("%d/%m/%Y")
    await edit_project(state, callback_query.from_user.id)
    await bot.send_message(chat_id=callback_query.from_user.id, text = 'Дата успешно изменена')
    await EditTasks.Get_inline_menu.set()


#если при создании проекта нужен файл, просим пользователя ввести имя, которое будет использоваться при хранении этого файла на диске
@dp.callback_query_handler(text = 'with_file', state = PlanThingsProcces.Calendar)
async def get_file_name(message:Message, state: FSMContext):
    await bot.send_message(chat_id=message.from_user.id,
                           text='Введите желаемое название файла <b> Картинку нужно загружать, как файл (в верхнее окошечко)</b>',parse_mode='HTML')
    await PlanThingsProcces.FileName.set()


#записываем имя файла и просим пользователя загрузить его
@dp.message_handler(state = PlanThingsProcces.FileName)
async def get_file_function(message: types.Message, state:FSMContext)->None:
    await bot.send_message(chat_id=message.from_user.id,
                           text = 'Загрузи файл',
                        reply_markup=ikb_cancel)
    async with state.proxy() as data:
        data['file_name'] = message.text
    await PlanThingsProcces.next()

#если файлы при создании проекта не нужны
@dp.callback_query_handler(text = 'without_file', state=PlanThingsProcces.Calendar)
async def dont_get_file_function(message:types.Message, state = FSMContext)->None:
    await bot.send_message(chat_id=message.from_user.id,
                           text = 'Введите время, когда Вам было бы удобно получить уведомление в формате HH:MM')
    await  PlanThingsProcces.NotificationTime.set()


#послений этам создания проекта и запись его в базу данных
@dp.message_handler(state=PlanThingsProcces.NotificationTime)
async def add_time_notification(message:Message, state: FSMContext)->None:
    async with state.proxy() as data_dict:
        data_dict['notification_time'] = message.text
    await create_project(state,message.from_user.id)
    users = get_users(message.from_user.id)
    users = list(users)
    flag = 0
    for us in users[0]:
        if us == str(message.from_user.id):
            flag = 1
    if flag == 0:
        print('dada')
        another_way('test_api_bot', str(message.from_user.id))
    await message.answer(text='Задание успешно создано!')
    await state.finish()


#обработчик загрузки файлов при создании проекта
@dp.message_handler(content_types = ['document','photo'], state = PlanThingsProcces.Document)
async def doc_handler(message: types.Message, state: FSMContext)-> None:
    async with state.proxy() as data:
        if document := message.document:
            await document.download(
                destination_file=f"{data['file_name']}",
            )
        upload_file_on_drive(str(message.from_user.id), data['project_name'][0], data['file_name'])
    await bot.send_message(chat_id=message.from_user.id,
                           text='Успешно! Файл загружен)',
                           reply_markup=ikb_files)

#кнопка добавить больше файлов
@dp.callback_query_handler(text='add_more_files', state=PlanThingsProcces.Document)
async def add_files(callback:CallbackQuery):
    await bot.send_message(chat_id=callback.from_user.id,text='Введите название файла в формате filename.txt (.docx, .txt .jpg), <b> Картинку нужно загружать, как файл </b>',parse_mode='HTML')
    await PlanThingsProcces.FileName.set()

#закончить добавление файлов
@dp.callback_query_handler(text='end_add_files', state=PlanThingsProcces.Document)
async def set_time(callback:CallbackQuery):
    await bot.send_message(chat_id=callback.from_user.id,
                           text='Введите время, когда Вам было бы удобно получить уведомление в формате HH:MM (например 14:00)')
    await  PlanThingsProcces.NotificationTime.set()


#сброс состояния
@dp.callback_query_handler(text='cancel', state=PlanThingsProcces)
async def cmd_start(message: types.Message, state: FSMContext)->None:
    await bot.send_message(text='Вы в главном меню', chat_id=message.from_user.id)
    await state.finish()


#Функция отвечает за отправку уведомлений пользователям.
@dp.message_handler()
async def notification_function():
    #выгружаем все задания, которые находятся в статусе "текущие"
    tasks = get_awaiting_tasks()
    for task in tasks:
        #проверяем не наступила ли дата и время уведомления.
        if check_for_notification(task[2], task[3]):
            #если наступило - отправляем уведомление
            await bot.send_message(chat_id=task[0], text=f"У вас запланировано важное дело - {task[1]}")
            #флажок, проверка на "периодичность дела"
            if task[4] == 0:
                #если дело не переодическое то заменяем стус "в ожидании" на "отправлено"
                await replace_await_by_send(task[0], task[1])
            else:
                #вычисляем новую дату для уведомления у периодических дел
                date_culc = select_date_task_for_periodic(task[0], task[1])
                res_date = add_days(date_culc[0], date_culc[1])
                #обнавляем дату периодического дела
                await update_date_task_for_pereodic(task[0], task[1], res_date)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True,
                           on_startup=on_startup)