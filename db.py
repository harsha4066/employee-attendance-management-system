import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="141.209.241.57",
        user="bhati1j",
        password="mypass",
        database="BIS698M1530_GRP7"
    )