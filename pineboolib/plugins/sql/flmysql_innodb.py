from pineboolib.plugins.sql.flmysql_myisam import FLMYSQL_MYISAM


class FLMYSQL_INNODB(FLMYSQL_MYISAM):

    version_ = None
    conn_ = None
    name_ = None
    alias_ = None
    errorList = None
    lastError_ = None

    def __init__(self):
        super(FLMYSQL_INNODB, self).__init__()
        self.name_ = "FLMYSQL_INNODB"
        self.alias_ = "MySQL INNODB (MYSQLDB)"
        self.noInnoDB = False
