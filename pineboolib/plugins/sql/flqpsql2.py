from pineboolib.utils import  checkDependencies
import logging

from sqlalchemy import create_engine

logger = logging.getLogger(__name__)
from pineboolib.plugins.sql.flqpsql import FLQPSQL


class FLQPSQL2(FLQPSQL):

    def __init__(self):
        super().__init__()
        self.name_ = "FLQPSQL2"
        self.alias_ = "PostgreSQL (PG8000)"
        self.mobile_ = True
        self.pure_python_ = True

    def useThreads(self):
        return False

    def useTimer(self):
        return True

    def safe_load(self):
        return checkDependencies({"pg8000": "pg8000", "sqlalchemy":"sqlAlchemy"}, False)

    def connect(self, db_name, db_host, db_port, db_userName, db_password):
        self._dbname = db_name
        checkDependencies({"pg8000": "pg8000", "sqlalchemy":"sqlAlchemy"})
        import pg8000
        
        

        conninfostr = "dbname=%s host=%s port=%s user=%s password=%s connect_timeout=5" % (
            db_name, db_host, db_port,
            db_userName, db_password)

        try:
            self.conn_ = pg8000.connect(user=db_userName, host=db_host, port=int(db_port), database=db_name, password=db_password, timeout=5)
            self.engine_ = create_engine('postgresql+pg8000://%s:%s@%s:%s/%s' % (db_userName, db_password, db_host, db_port, db_name))
        except Exception:
            import pineboolib
            if not pineboolib.project._DGI.localDesktop():
                import traceback
                if repr(traceback.format_exc()).find("the database system is starting up") > -1:
                    raise
                    
                return False
            
            pineboolib.project._splash.hide()
            if repr(traceback.format_exc()).find("does not exist") > -1:
                ret = QMessageBox.warning(None, "Pineboo",
                                          "La base de datos %s no existe.\n¿Desea crearla?" % db_name,
                                          QMessageBox.Ok | QMessageBox.No)
                if ret == QMessageBox.No:
                    return False
                else:
                    try:
                        tmpConn = pg8000.connect(user="postgres", host=db_host, port=int(db_port), password=db_password, timeout=5)
                        tmpConn.autocommit = True

                        cursor = tmpConn.cursor()
                        try:
                            cursor.execute("CREATE DATABASE %s" % db_name)
                        except Exception:
                            print("ERROR: FLPSQL.connect",
                                  traceback.format_exc())
                            cursor.execute("ROLLBACK")
                            cursor.close()
                            return False
                        cursor.close()
                        return self.connect(db_name, db_host, db_port, db_userName, db_password)
                    except Exception:
                        qWarning(traceback.format_exc())
                        QMessageBox.information(
                            None, "Pineboo", "ERROR: No se ha podido crear la Base de Datos %s" % db_name, QMessageBox.Ok)
                        print(
                            "ERROR: No se ha podido crear la Base de Datos %s" % db_name)
                        return False
            else:
                QMessageBox.information(
                    None, "Pineboo", "Error de conexión\n%s" % str(e), QMessageBox.Ok)
                return False

        # self.conn_.autocommit = True #Posiblemente tengamos que ponerlo a
        # false para que las transacciones funcionen
        #self.conn_.set_isolation_level(
        #    pg8000.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        
        self.conn_.autocommit = True

        if self.conn_:
            self.open_ = True

        try:
            cursor = self.conn_.cursor()
            cursor.execute("SET CLIENT_ENCODING TO 'UTF8'")
        except Exception:
            qWarning(traceback.format_exc())

        return self.conn_