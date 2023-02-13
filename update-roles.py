import csv
import json
import os
import psycopg2
import sys
from credentials.secret_file import DB_PASSWORD
from credentials.secret_file import DB_DATABASE
from credentials.secret_file import DB_HOST
from credentials.secret_file import DB_PORT
from credentials.secret_file import DB_USER

# this script converts users to any specified role as long as their emails
# are a txt document
#
# last updated 2/13/2023 by Kyle Wade
def main(argv):

    valid_roles = {'inductee',
                   'member',
                   'officer',
                   'admin'}
    
    if len(sys.argv) != 3:
        print("Usage: python update-roles.py <email file> <inductee, member, officer, admin>")
        exit(1)
    if os.path.isfile(sys.argv[1]) is False:
        print("" + sys.argv[1] + " is not a valid file.")
        exit(1)
    if sys.argv[2] not in valid_roles:
        print("" + sys.argv[2] + " is not a valid role.")
        exit(1)
    try:
        # print(DB_USER)
        # print(DB_PASSWORD)
        # print(DB_HOST)
        # print(DB_PORT)
        # print(DB_DATABASE)
        connection = psycopg2.connect(user=DB_USER,
                            password=DB_PASSWORD,
                            host=DB_HOST,
                            port=DB_PORT,
                            database=DB_DATABASE)
        cursor = connection.cursor()
        print("Database connected!")
    
        emails_list = []
        emails_file_path = sys.argv[1]
        print("Opening ", emails_file_path)
        with open(emails_file_path) as f:
            for line in f:
                line = line.strip()
                emails_list.append(line)
        print("Looping through emails\n")

        sql_in_clause = "("
        for email in emails_list:
            sql_in_clause = sql_in_clause + "'" + email + "', "
        sql_in_clause = sql_in_clause[:len(sql_in_clause) - 2]
        sql_in_clause = sql_in_clause + ")"

        sql_get_user_ids = "SELECT \"id\" FROM app_user WHERE \"email\" IN " + sql_in_clause
        cursor.execute(sql_get_user_ids)

        records = cursor.fetchall()

        id_list = []
        for id in records:
            id_list.append(id[0])
        
        sql_in_clause = "("
        for id in id_list:
            sql_in_clause = sql_in_clause + "" + str(id) + ", "
        sql_in_clause = sql_in_clause[:len(sql_in_clause) - 2]
        sql_in_clause = sql_in_clause + ")"

        sql_update_user_roles = "UPDATE app_user SET \"role\"=\'" + sys.argv[2] + "\' WHERE \"id\" in " + sql_in_clause
        sql_update_user_attendance = ""

        if sys.argv[2] == "inductee":
            sql_update_user_attendance = "UPDATE attendance SET \"isInductee\"=\'true\' WHERE \"attendeeId\" in " + sql_in_clause

        else:
            sql_update_user_attendance = "UPDATE attendance SET \"isInductee\"=\'false\' WHERE \"attendeeId\" in " + sql_in_clause

        cursor.execute(sql_update_user_roles)
        cursor.execute(sql_update_user_attendance)
        connection.commit()

        print("Successfully updated users to " + sys.argv[2])

    except psycopg2.Error as e:
        print("Error reading data from SQL table", e)
        if (connection):
            cursor.close()
            connection.close()
            print("Closed Database Connection")
        exit
    except e:
        print("A non-database exception occured!")
        print(e)
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("Closed Database Connection")

if __name__ == "__main__":
    main(sys.argv[1:])