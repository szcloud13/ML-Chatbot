# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import sqlite3
from flask import request, g, jsonify

from . import Resource
from .. import schemas


def returnResults(tuple_list):
    info = []
    print('in return reults')
    for i in tuple_list:
        print(i[1], i[2], i[3])
        dentist = {}
        dentist['name'] = i[1]
        dentist['location'] = i[2]
        dentist['specialization'] = i[3]
        info.append(dentist)
    
    print('returning ')
    print(info)

    return info


class Dentists(Resource):
    def get(self):
        print(g.args)
        print(request.args['expression'])
        expression = request.args['expression']

        dentists = []
        try:
            conn = sqlite3.connect('dentists.db') # make sure db is in /dentists directory
            print("connected to db")

            if(expression == 'any'): # get every dentists on db
                cursor = conn.execute("SELECT name, location, specialization from dentists")
                for row in cursor:
                    dentist_info = {}
                    dentist_info['name'] = row[0]
                    dentist_info['location'] = row[1]
                    dentist_info['specialization'] = row[2]
                    print(dentist_info)
                    dentists.append(dentist_info)
                conn.close()
                return dentists, 200, None

            else:
                # cursor = conn.execute("SELECT * FROM dentists WHERE name LIKE '%s'" % dentist_name)
                cursor = conn.execute("SELECT * FROM dentists WHERE name LIKE '%s'" % ('%'+expression+'%'))
                dentist_list = cursor.fetchall()
                
                if len(dentist_list) == 0:  
                    # check if its querying for location
                    cursor = conn.execute("SELECT * FROM dentists WHERE location LIKE '%s'" % ('%'+expression+'%'))
                    location = cursor.fetchall()

                    if len(location) == 0:
                        cursor = conn.execute("SELECT * FROM dentists WHERE specialization LIKE '%s'" % ('%'+expression+'%'))
                        specialization = cursor.fetchall()

                        if len(specialization) == 0:
                            conn.close()
                            return "No such dentist, location, specialization found", 403
                        
                        else:
                            print(specialization[0])
                            conn.close()
                            return returnResults(specialization), 200

                    else: 
                        print(location[0])
                        conn.close()
                        return returnResults(location), 200
            
                else:
                    print(dentist_list[0])
                    print(type(dentist_list))
                    conn.close()
                    return returnResults(dentist_list), 200
        except:
            return "Cannot find the database in demo directory", 400
        
