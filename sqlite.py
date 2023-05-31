import sqlite3 as sq
from upload_google_drive import another_way


# создание базы данных
async def db_start():
    global db, cur

    db = sq.connect('new_db')
    cur = db.cursor()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS tasks(user_id TEXT, project_name TEXT, project_description TEXT, project_date DATE,notific_time TEXT ,status TEXT, done_or_not INTEGER,periodic INTEGER, PRIMARY KEY (user_id, project_name) ) ")
    db.commit()



def get_projects_name_for_user(user_id):
    data = cur.execute("SELECT project_name FROM tasks WHERE user_id = {id}".format(id=user_id)).fetchall()
    return data


async def create_project(state, user_id):
    async with state.proxy() as data_dict:
        user = cur.execute("SELECT 1 FROM tasks WHERE project_name == '{key}' and user_id == '{id}'".format(id=user_id,
                                                                                                            key=
                                                                                                            data_dict[
                                                                                                                'project_name'][
                                                                                                      0])).fetchone()
        if not user:
            cur.execute("INSERT INTO tasks VALUES(?, ?, ?, ?, ?,?,?,?)", (
            user_id, data_dict['project_name'][0], data_dict['description'][0], data_dict['project_date'], data_dict['notification_time'],'awaiting', 0, 0))
            db.commit()


async def edit_project(state, user_id):
    async with state.proxy() as data:
        cur.execute("UPDATE tasks SET project_date = '{}' WHERE project_name == '{}'and user_id == '{user_id}'".format(
            data['date'], data['name'], user_id=user_id))

        db.commit()

def get_users(user_id):
    users = cur.execute("SELECT DISTINCT user_id FROM tasks").fetchall()
    return users


async def edit_state_of_task(state, user_id,flag):
    async with state.proxy() as data:
        cur.execute(
            "UPDATE tasks SET done_or_not = '{flag}',project_date = '',notific_time= '' WHERE project_name == '{}'and user_id == '{user_id}'".format(
                data['name'],
                flag=flag,
                user_id=user_id))
    db.commit()


async def get_state_of_task(state, user_id):
    async with state.proxy() as data:
        done = cur.execute("SELECT done_or_not FROM tasks WHERE project_name == '{}'and user_id == '{user_id}'".format(
            data['name'],
            user_id=user_id)).fetchone()
        return done[0]


def get_done_tasks(user_id):
    done_tasks = cur.execute("SELECT * FROM tasks WHERE user_id = {user_id} and done_or_not = 0 ORDER BY project_date".format(user_id=user_id)).fetchall()
    return done_tasks

def get_not_done_tasks(user_id):
    not_done_tasks = cur.execute("SELECT * FROM tasks WHERE user_id = {user_id} and done_or_not = 1 ORDER BY project_date".format(user_id=user_id)).fetchall()
    return not_done_tasks

async def edit_task_description(state, user_id):
    async with state.proxy() as data:
        cur.execute("UPDATE tasks SET project_description = '{desc}' WHERE user_id = '{id}' and project_name = '{name}' "\
            .format(desc = data['description'], id = user_id, name = data['name']))
    db.commit()

async def edit_task_time(state, user_id):
    async with state.proxy() as data:
        cur.execute("UPDATE tasks SET notific_time = '{time}' WHERE user_id = '{id}' and project_name = '{name}' "\
            .format(time = data['notification_time'], id = user_id, name = data['name']))
    db.commit()



async def delete_my_task(state, user_id):
    async with state.proxy() as data:
        cur.execute("DELETE FROM tasks WHERE user_id = '{user_id}' and project_name='{project_name}'".format(user_id=user_id, project_name=data['name']))
    db.commit()


def get_awaiting_tasks():
    awaiting_tasks = cur.execute("SELECT user_id, project_name,project_date, notific_time,periodic FROM tasks WHERE status = 'awaiting' and done_or_not = '0' ").fetchall()
    return awaiting_tasks

async def replace_await_by_send(user_id, project_name):
    cur.execute("UPDATE tasks SET status = 'send' WHERE user_id = '{id}' and project_name = '{name}'".format(id = user_id, name = project_name))
    db.commit()

def select_date_task_for_periodic(user_id, project_name):

    for_new_date_calc = cur.execute("SELECT project_date, periodic FROM tasks WHERE user_id = '{id}' and project_name = '{name}'".format(id = user_id, name = project_name)).fetchone()
    return for_new_date_calc

async def update_date_task_for_pereodic(user_id, project_name,res_date):
    cur.execute("UPDATE tasks SET project_date = '{date}' WHERE user_id = '{id}' and project_name = '{name}'".format(date = res_date,id = user_id, name = project_name))
    db.commit()

async def get_periodic_state(state,user_id):
    async with state.proxy() as data:
        period = cur.execute("SELECT periodic FROM tasks WHERE user_id = '{id}' and project_name = '{name}'".format(id=user_id, name=data['name'])).fetchone()
        return period

async def update_pereodic_of_task_yes(user_id, state,period):
    async with state.proxy() as data:
        cur.execute("UPDATE tasks SET periodic= '{}' WHERE user_id = '{}' and project_name = '{}'".format(period ,user_id, data['name']))
    db.commit()

async def update_pereodic_of_task_no(user_id, project_name):

    cur.execute("UPDATE tasks SET periodic = 0 WHERE user_id = '{id}' and project_name = '{name}'".format(id = user_id, name = project_name))
    db.commit()