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

# this script converts users to any specified induction class as long as their emails
# are in a txt document
#
# last updated 2/13/2023 by Kyle Wade
def main(argv):
    
    if len(sys.argv) != 3:
        print("Usage: python update-induction-class.py <email file> <induction_class_quarter>")
        exit(1)
    if os.path.isfile(sys.argv[1]) is False:
        print("" + sys.argv[1] + " is not a valid file.")
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

        sql_query_get_induction_class = "SELECT * FROM induction_class WHERE \"quarter\"=\'"+sys.argv[2]+"\'"
    
        cursor.execute(sql_query_get_induction_class)

        record = cursor.fetchone()

        if record is None:
            print(sys.argv[2] + " induction class does not exist!")
            exit(1)
        

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

        update_induction_class_emails = "UPDATE app_user SET \"inductionClassQuarter\"=\'"+ sys.argv[2] + "\' WHERE \"email\" IN " + sql_in_clause
        cursor.execute(update_induction_class_emails)

        connection.commit()

    except psycopg2.Error as e:
        print("Error reading data from SQL table", e)
        if (connection):
            cursor.close()
            connection.close()
            print("Closed Database Connection")
        exit
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("Closed Database Connection")

if __name__ == "__main__":
    main(sys.argv[1:])