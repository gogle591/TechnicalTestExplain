import psycopg2
import traceback
import json
dbname= input(" Saisir le nom de votre base de donnée:\n")
username = input(" Saisir le nom de votre utilistauer (username):\n")
password = input("Saisir votre mot de passe:\n ")


def make_position(role,territory_code,territory_name,start_date,end_date):
    if (end_date == None):
        return {
        "role": role,
        "territory_code": territory_code,
        "territory_name": territory_name,
        "start_date": str(start_date)
        }
    else:
        return {
        "role": role,
        "territory_code": territory_code,
        "territory_name": territory_name,
        "start_date": str(start_date),
        "end_date": str(end_date)
        }

def make_positions(id_physical_person, cursor):
    positions = []
    cursor.execute("SELECT role, start_date, end_date, legal_entity_id from position where  physical_person_id = '{}' ORDER BY start_date;".format(id_physical_person))
    rows = cursor.fetchall()
    for position in rows:
        cursor.execute("SELECT code, name from location where id = (SELECT location_id from legal_entity where id ='{}' ); ".format(position[3]))
        location = cursor.fetchall()[0]
        role = position[0]
        territory_code = location[0]
        territory_name = location[1]
        start_date = position [1]
        end_date =  position[2]
        positions.append(make_position(role,territory_code,territory_name,start_date,end_date))
    
    return positions

def make_impacter(id,name,positions):
    return {
        "id": id,
        "name": name,
        "positions": positions 
    }

def make_impacters(person_ids, cursor):
    impacters = []
    for id_physical_person in person_ids:
        cursor.execute("SELECT firstname, lastname, impacter_id from physical_person where id = '{}';".format(id_physical_person[0]))
        impacter = cursor.fetchall()[0]
        name = impacter[0] + " "+ impacter[1]
        cursor.execute("SELECT surname_text from surname where impacter_id = '{}'".format(impacter[2]))
        id = cursor.fetchall()[0][0]
        positions = make_positions(str(id_physical_person[0]),cursor)
        impacters.append(make_impacter(id,name,positions))
    return impacters
    

        

    

try:
    connect_str = "dbname='{}' user='{}' host='localhost' password='{}'".format(dbname,username,password)
    # use our connection values to establish a connection
    conn = psycopg2.connect(connect_str)
    # create a psycopg2 cursor that can execute queries
    cursor = conn.cursor()
    # create a new table with a single column called "name"
    cursor.execute("""SELECT DISTINCT physical_person_id from position where NOW()::timestamp::date < end_date;""")
    conn.commit() 
    person_ids = cursor.fetchall()
    impacters = make_impacters(person_ids,cursor)
    jsonfile = {
        "impacters": impacters
    }
    with open("mendat_encours.json", "w", encoding="utf-16") as outfile:  
        json.dump(jsonfile, outfile, indent=4, ensure_ascii=False) 
    cursor.close()
    conn.close()
except Exception as e:
    print("Error :{}".format(e))
    print(traceback.format_exc())