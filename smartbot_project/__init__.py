"""
SmartBot Project Package.
Includes PyMySQL fallback initialization for seamless MySQL connectivity
with XAMPP across Windows, macOS, and Linux.
"""

# Attempt to configure PyMySQL as the MySQLdb driver if mysqlclient is not natively loaded
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
