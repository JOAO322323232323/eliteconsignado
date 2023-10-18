import requests, json, pandas, sqlite3, threading, time

class FGTS_LOTE(object):

    def __init__(self):
        self.connection = sqlite3.connect('fgts_facta.db')
        self.c = self.connection.cursor()

    def lock_database(self, cursor, codigo, commit=False):
        lock = threading.Lock()
        res = 'again'
        try:
            lock.acquire(True)
            res = cursor.execute(codigo)
            if commit:
                self.connection.commit()
        except:
            lock.release()
            return 'again'
        finally:
            lock.release()
            return res