import pymysql

#Fake the version number so Django thinks it is using a newer driver
pymysql.version_info = (2, 2, 7, "final", 0)

#Tell Django to use pymysql as the driver
pymysql.install_as_MySQLdb()
