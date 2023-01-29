import datetime  # для фиксации времени записи
import sqlite3  # Импорт библиотеки


class GameResult():
    def __init__(self):
        self.con = sqlite3.connect('scores_db.db')  # Подключение к БД
        # Примечание: файл БД должен находиться в одном каталоге со скриптом
        self.cur = self.con.cursor()  # Создание курсора (конструктор подключил к БД)

    def get_results(self):  # Выполнение запроса и получение всех результатов
        result = self.cur.execute("""SELECT * FROM results""").fetchone()
        return result

    def set_results(self, scores, shots, success, boss_pass):  # Выполнение запроса и занесение результатов
        # получим дату и время
        now = datetime.datetime.now()
        time = now.strftime('%d.%m.%Y %H:%M')
        ok = self.cur.execute("""DELETE FROM results""")  # сначала удаляем старую запись
        query = f'INSERT INTO results VALUES (1, {scores}, {shots}, {success}, "{boss_pass}", "{time}")'
        result = self.cur.execute(query)
        self.con.commit()
        return result

    def disconnect(self):
        self.con.close()
