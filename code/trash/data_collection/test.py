from PyQt5.QtSql import QSqlDatabase,QSqlTableModel,QSqlQuery,QSqlQueryModel

sdb = QSqlDatabase.addDatabase("QSQLITE")
sdb.setDatabaseName("F:\\Current proj's\\ddos attack\\proj\\data_collection\\19.09.db")
if sdb.open() == False:
    print('no')
zapr = "select * from learn"
sql = QSqlQuery(sdb)
sql.exec(zapr)
print(sql.lastError().text())
while sql.next():
    print(sql.)