# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
import datetime as DT
from flask import request, g, jsonify
import os 
import json
import requests
from requests.exceptions import HTTPError
from rivescript import RiveScript
from . import Resource
from .. import schemas



def requestDentist(dentist):
    try:
        # TODO: CHange port number if different
        url = 'http://127.0.0.1:8081/dentist_api/dentists?expression=' + dentist
        response  = requests.get(url)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred in requestDentist: {err}')  # Python 3.6
    else:
        print('Success in requestDentist!')
        dentist_list = response.json()
        print(dentist_list)
        returnStr = 'Our services available are: \n'
        for d in dentist_list:
            s = ' Dr. '
            s += d.get('name') +' who '
            s += 'specialized in ' + d.get('specialization')
            s += ', located in ' + d.get('location')
            returnStr += s + '. \n'
            print(d)

        returnStr += "Our opening hours are 9am-5pm, 7 days a week."
        return returnStr


class Ask(Resource):

    def get(self):

        query = request.args.get('expression')
        print(query)
        query = query.lower() 
        if query == '':
            return bot_replies(''), 200
        try:
            url = 'https://api.wit.ai/message?v=20201110&q=' + query
            response  = requests.get(
                url,
                headers={'Authorization': 'Bearer YAJKOQ53TWEQEU2PE76RJK2LXMUFP2PF'},
            )
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Python 3.6
        except Exception as err:
            print(f'Other error occurred: {err}')  # Python 3.6
        else:
            print('Success in getting wit.ai !')
            print(response.json())

            try:
                data = (response.json()).get('intents')
                keywords = (response.json()).get('entities')
                try: 
                    intent = data[0].get('name')
                except: # no intent detected
                    # check if it is a greeting
                    # if keywords.get("wit_greetings:wit_greetings") and len(keywords.get("wit_greetings:wit_greetings")) > 0:
                    reply = bot_replies(query)
                
                    if reply == None:
                        print('RiveScript error')
                        return 'RiveScript error', 400
                    else:
                        return reply, 200

                            
    #*** Booking only: to further encapsulate utterance meaning in case bot got it wrong 
                utterances = []
                if keywords.get('wit_bookings:wit_bookings'):
                    # get booking related entities identified
                    booking_wit = keywords.get('wit_bookings:wit_bookings')
                    for x in booking_wit:
                        if 'cancel' in x.get('value') or 'cannot make' in x.get('value'):
                            intent = 'CancelBooking' # to enforce chatbot understanding if utterance too complicated
                        utterances.append(x.get('value').lower())

                if keywords.get('wit$contact:contact'):
                    wit_contact = keywords.get('wit$contact:contact')
                    for x in wit_contact:
                        if 'he' in x.get('value'):
                            return "Please specify who do you mean by 'he'. So I can be of better service :)", 400

                
    #### categorize action based on intent ####

                if intent == 'Dentists':
                    # call dentist api to get identified dentist
                    try:
                        dentist_list = (keywords.get("wit_dentists:wit_dentists"))
                        dentist = whichDentist(dentist_list)

                        if dentist == False: # input was wrong
                            return 'Sorry I could not find a dentist for you :(', 200
                    except: # if wit_dentists:wit_dentists is empty
                        dentist = ' ' # just get every dentists available
                        pass
                    
                    # form reply string with dentist info
                    info = requestDentist(dentist)
                    if info == '':
                        return 'Sorry I could not find a dentist for you :(', 200
                    return info, 200

                elif intent == 'Booking':

                    error_msg = "Please include these details in a sentence if you are booking an appointment: your full name, the dentist's name, preferred time and date.\n Please note our dentists take bookings for an hour only."
                    
                    if keywords.get("wit$datetime:datetime") and len(keywords.get("wit$datetime:datetime")) > 1:
                        # bot understanding made datetime provided not analyzable 
                        return "Please specify one date and time together and uniformly, Try [eg. 14th Nov around 10am] ", 400

                    time_of_day = ''
                    day_of_week = ''
                    dentist_name = ''
                    patient_name = ''
                        
                    try:
                        if 'earliest' in utterances or 'as soon as possible' in utterances or 'when' in utterances or 'available' in utterances or 'is there any' in utterances or 'free' in utterances:
                            # if a dentist filter is given
                            if keywords.get("wit_dentists:wit_dentists"):
                                dentist_list = (keywords.get("wit_dentists:wit_dentists"))
                                dentist_name = whichDentist(dentist_list)
                                # check if a date time is specified as well
                                if keywords.get("wit$datetime:datetime"):
                                    time_of_day, day_of_week, date_booking = validateDateTime(keywords)
                                    # filtered availabilities based on all three filters
                                    
                                    if time_of_day != False:
                                        resp_status, reply = findBooking(time_of_day, day_of_week, dentist_name)
                                        if resp_status == True:
                                            return reply, 200 
                                        else:
                                            return reply, 400
                                    # error msg is returned instead
                                    return day_of_week, 400
                                else:
                                    # filter availabilites based on a dentist only
                   
                                    resp_status, reply = findBooking('', '', dentist_name)
                                    if resp_status == True:
                                        return reply, 200 
                                    else:
                                        return reply, 400

                            elif keywords.get("wit$datetime:datetime"):
                                time_of_day, day_of_week, date_booking = validateDateTime(keywords)
                                if time_of_day != False:
                                    resp_status, reply = findBooking(time_of_day, day_of_week, '')
                                    if resp_status == True:
                                        return reply, 200 
                                    else:
                                        return reply, 400 
                                # error msg is returned instead
                                return day_of_week, 400
                                # filter availabilites based on a date/time only
                            else:    
                                # get any earliest
                                resp_status, reply = findBooking('','', '')
                                if resp_status == True:
                                    return reply, 200 
                                else:
                                    return reply, 400 

                    except Exception as e:
                        print(e)
                        return "Sorry I could not find an appointment available right now. Thank you for choosing our service!", 400

                    # if its not asking for availabilities, then user is trying to make a booking
                    # strict check & extract whether if there's a dentist value included 
                    try:  
                        dentist_list = (keywords.get("wit_dentists:wit_dentists"))
                        dentist_name = whichDentist(dentist_list) 
                    except:
                        return "No worries! I just can't seem to find a dentist specified. Or ask me 'what dentists are available?' to know more! :) \n"+ error_msg, 400
           
                    try:    
                        # if a dentist value is not provided, prompt user to reenter details
                        if dentist_name == ' ' or dentist_name == '':
                            return "No worries! I just can't seem to find a dentist specified by you. Or ask me 'what dentists are available?' to know more! :)\n"+error_msg, 400

                        # check and extract whether if patient name is provided
                        try:
                            patient_name = (keywords.get("wit$contact:contact"))[0].get('value')
                        except:
                            return "No worries! I just can't seem to identify your full name.\n" + error_msg, 400

                        try: 
                            
                            # check if date & time is valid
                            time_of_day, day_of_week, date_booking = validateDateTime(keywords)
                            if time_of_day != False:
                                # attempt to book the appointment given a dentist provided, a valid date & time given
                                resp_status, reply = requestBooking(day_of_week, time_of_day, dentist_name, patient_name, date_booking)
                                
                                if resp_status != False:                                    
                                    return reply, 200
                                else:
                                    return reply, 400
                            else:
                                return day_of_week, 400
                                #return "The date/time provided is not valid. Try [eg. 14th Nov around 10am].\n Please include these details in a sentence when making a booking: your full name, the dentist's name, time (24hh:mmPM), date.", 400
                        except:
                            return "No worries! I just can't seem to find a valid date/time in your booking request. Try [eg. 14th Nov around 10am] or ask me for availabilities!\n " + error_msg, 400
                    
                    # else:
                    except:    
                        return 'Please rephrase again, I could not understand. :(', 400

                elif intent == 'CancelBooking':
                    dentist_name = ''
                    patient_name = ''
                    time_of_day = ''
                    day_of_week = ''

                    error_msg = "Please include these details in a sentence when cancelling an appointment: your full name, the dentist's name, time and date."
                    # check & extract whether if there's a dentist value included 
                    try:  
                        dentist_list = (keywords.get("wit_dentists:wit_dentists"))
                        dentist_name = whichDentist(dentist_list) 
                    except:
                        return "May I ask which dentist the appointment was with? " + error_msg, 400
                
                    # check and extract whether if patient name is provided
                    try:
                        patient_name = (keywords.get("wit$contact:contact"))[0].get('value')
                    except:
                        return "May I ask for your full name? " + error_msg, 400

                    try:
                        time_of_day, day_of_week, bookingdate_str = validateDateTime(keywords)
                        if time_of_day == False:
                            return day_of_week + error_msg, 400
                    except:
                        return error_msg + ' \nPlease note only valid bookings in the next 7 days can be cancelled.', 400

                   
                    resp_status, reply = cancelBooking(day_of_week, time_of_day, dentist_name, patient_name, bookingdate_str)
                    if resp_status != False:
                        return reply, 200
                    else:
                        return reply, 400

                else:
                    
                    if bot_replies(query) == None:
                        print('RiveScript error')
                        return 'RiveScript error', 400
                    else:
                        return bot_replies(query), 200
            except Exception as e: 
                print(e)
                return "Sorry I cannot understand your intentions, please kindly rephrase :)", 400
        
        return None, 200, None

def validateDateTime(keywords):
   
    try:

        if (keywords.get("wit$datetime:datetime"))[0].get('body'):
            input_date = (keywords.get("wit$datetime:datetime"))[0].get('body')
            if 'today' in input_date:
                return False, "I'm sorry no bookings can be made on the same day. All bookings start tomorrow.", None

        if (keywords.get("wit$datetime:datetime"))[0].get('value'):
            # ensure a time/date entity is given for a booking
            date = (keywords.get("wit$datetime:datetime"))[0].get('value')
            date_str = date.split('T')  

        elif (keywords.get("wit$datetime:datetime"))[0].get('values'): 
            # user have given a range of time instead: eg. afternoon
            range_datetime = (keywords.get("wit$datetime:datetime"))[0].get('values')
            date = range_datetime[0].get('from')
            print(date)
            date_str = date.get('value').split('T')

        else:
            return False, 'No datetime found!'
        
        print(date_str)
        
        if len(date_str) < 2: # if a date and time are not identified in the right format through bot
            return False, "I can't seem to find a valid date/time specified. Try [eg. 14th Nov around 10am] or ask me for availabilities!\n ", None
   
        
        # get the date requested
        date_object = DT.datetime.strptime(date_str[0], '%Y-%m-%d').date()

        # date in a week from now
        date_valid = DT.date.today() + DT.timedelta(days=7)
      
        # check that this date is within a week starting from tomorrow
        if date_object < date_valid and date_object > DT.date.today():
            # date of booking is valid, checking time ...
            
            try:
                default = DT.time(0,00)
                start = DT.time(9, 00)
                end = DT.time(17, 00) 
                time_str = date_str[1].split('.')
                time_object = DT.datetime.strptime(time_str[0], '%H:%M:%S').time()
                
                # checking if the time is within operating hours
                if time_object >= start and time_object < end:
                    
                    # extract time of day & day of week info for the booking
                    time_of_day = time_object.strftime('%H:%M')
                    time_of_day += time_object.strftime('%p') # HH:MM AM/PM 
                    day_of_week = date_object.strftime('%A') # Monday, Tuesday ....

                    print(time_of_day, day_of_week, date_str[0])
                    return time_of_day, day_of_week, date_str[0]

                elif time_object == default: # default 12 AM if no time provided
                    print(date_object.strftime('%A'))
                    return '', date_object.strftime('%A'), date_str[0]
                    pass
                else:
                    print(time_object, start, time_object, end)
                    return False, "The requested booking time is not within our operating hours 9am - 5pm. \n Remember to include these details in a sentence if you are booking an appointment: your full name, the dentist's name, time (24hh:mmPM), date.", None
            except Exception as e:
                print(e)
                return False, "Something is wrong about the booking time", None
        
        elif date_object == DT.date.today(): 
            # edge case: when user vaguely mentioned "Tomorrow" only
            # what the user really mean:

            if keywords.get('wit_bookings:wit_bookings'):
                # get booking related entities identified
                date_wit = keywords.get('wit$datetime:datetime')
                for x in date_wit:
                    if x.get('body') and 'tomorrow' in x.get('body'):

                        time_str = date_str[1].split('.')
                        time_object = DT.datetime.strptime(time_str[0], '%H:%M:%S').time()
                        
                        date_tmw = DT.date.today() + DT.timedelta(days=1) # tommorrow
                        day_of_week = date_tmw.strftime('%A') # Monday, Tuesday...
                        date_appt = date_tmw.strftime('%Y-%m-%d') # 2020-11-14 etc
                        # time_of_day = DT.time(9,00).strftime('%H:%M') # defaults to start from 9am 
                        # time_of_day += DT.time(9,00).strftime('%p') # HH:MM AM/PM 

                        if time_object == DT.time(0,00): # only 'tomorrow' or 'tomorrow morning' is given
                            print('', day_of_week, date_appt)
                            return '', day_of_week, date_appt

                        elif time_object > DT.time(17,00):
                            return False, "The requested booking time is not within our operating hours 9am - 5pm. \n Remember to include these details in a sentence if you are booking an appointment: your full name, the dentist's name, time (24hh:mmPM), date.", None

                        else: # cases for 'tomorrow afternoon' etc
                            time_of_day = time_object.strftime('%H:%M')
                            time_of_day += time_object.strftime('%p') # HH:MM AM/PM 
                            print(time_of_day, day_of_week, date_appt)
                            return time_of_day, day_of_week, date_appt
                            

        else:
            return False, "Sorry, I couldn't identify a valid date/time or the date is not within the next 7 days. \nBookings can only be made for the next 7 days starting from tomorrow.\n Try [eg. 14th Nov around 10am] or ask me for availabilities!\n" , None

    except Exception as e: 
        print(e)
        return False, "I can't seem to find a valid date/time specified. Try [eg. 14th Nov around 10am] or ask me for availabilities!\n Please include these details in a sentence if you are booking an appointment: your full name, the dentist's name, time (24hh:mmPM), date.", None


def bot_replies(query):
    
    print(os.path.dirname(os.path.realpath(__file__)))
    bot = RiveScript()
    # bot.load_directory("service/demo/MLChatBot/api/brain") 
    # current path: /home/liyeez/COMP9322/ass2/chatbot/demo/MLChatBot/api
    bot.load_directory("demo/MLChatBot/api/brain")
    bot.sort_replies()
    reply = bot.reply("localuser", query)
    
    if reply != '':
        print(reply)
        return reply
    return None

def whichDentist(dentist_list):
    
    if dentist_list == None:
        return ' '
    else:
        # return once the first doctor name is identified
        print(len(dentist_list))
        for x in dentist_list:
            dentist = x.get('body').lower()
            print(dentist)
            if 'john' in dentist or 'smith' in dentist:
                return 'John'
            elif 'chang' in dentist or 'low ying' in dentist:
                return 'Chang'
            elif 'asman' in dentist or 'nematallah' in dentist:
                return 'Asman'
            else:
                dentist = ' ' # used by api to retrieve all dentists
    
        return dentist

def requestBooking(day_of_week, time_of_day, dentist_name, patient_name, date_appt): 
    print('in requestBooking')
    print(day_of_week, time_of_day)
    try:
        # TODO: CHange port number if different
        url = 'http://127.0.0.1:8082/timeslot_api/appointments'
        headers = {'Content-type': 'application/json'}
        data = {
                    'time_of_day': time_of_day,
                    'day_of_week': day_of_week,
                    'dentist_name': dentist_name,
                    'patient_name': patient_name,
                    'status': False, # False to reserve the spot
                    'date_appt': date_appt
                }
                
        response  = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
    except HTTPError as http_err:
        print(response.text)  # Python 3.6
        try:
            rec = json.loads(response.text)
            if "reserved" in rec.get('err'):
                try:   
                    booking = rec.get('recommendation')
                    reply = 'Sorry this booking slot is already reserved! How about this:' +  '\n'
                    reply += 'Next ' +booking.get('day_of_week') + ' '+ booking.get('date_appt')  + ' ' + booking.get('time_of_day')
                    reply += ' with Dr ' + booking.get('dentist_name') + '. \nAs always, please include all essential details when making a booking!'

                    return False, reply
                except:
                    pass
            return False, "Sorry it's already reserved and I can't seem to find any booking slot to recommend. Try another date or time?"
        except:
            return False, response.text

    except Exception as err:
        print(err)  # Python 3.6
        return False, err
    else:
        print('Success in requestBooking!')
        print(response.json())
        try:
            booking = response.json().get('appointment')
            reply = 'No worries, ' + patient_name +'! I have successfully booked you in for: \n'
            reply += 'Next ' + booking.get('day_of_week') + ' '+booking.get('date_appt') + ' ' + booking.get('time_of_day')
            reply += ' with Dr ' + booking.get('dentist_name') + '. Thank you for choosing our dental service!'
        
            print(reply)
            return True, reply
        except:
            return False, ''

        
# get request to timeslot api
def findBooking(time_of_day, day_of_week, dentist_name):
    time_of_day = str(time_of_day)
    day_of_week = str(day_of_week)

    print('in find booking')
    print(time_of_day, day_of_week, dentist_name)
    
    try: 
        url = 'http://127.0.0.1:8082/timeslot_api/appointments'
        
        if day_of_week != '':
            url += '?'+ 'day_of_week='+ day_of_week

            if time_of_day != '':
                url += '&' + 'time_of_day=' + time_of_day
        
            if dentist_name != '':
                 url += '&' + 'dentist_name=' + dentist_name
       
        elif time_of_day != '':
            url += '?' + 'time_of_day=' + time_of_day

            if dentist_name != '':
                url += '&' + 'dentist_name=' + dentist_name

        elif dentist_name != '':
            url += '?' + 'dentist_name=' + dentist_name
        
        print(url)
        response  = requests.get(url)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred in findBooking: {err}')  # Python 3.6
    else:
        print('Success in findBooking!')
        # print(response.json())
        if response.json().get('appointments') and len(response.json().get('appointments')) > 0:
            reply = 'The timeslots that suits your criteria are: \n'
            for x in response.json().get('appointments'):
                print(x)
                try:
                    reply += x.get('day_of_week') + ', ' + x.get('date_appt')+ ', ' + x.get('time_of_day') + ' with Dr ' + x.get('dentist_name') + ', \n'
                except:
                    print('missing fields!')
                    return False, "Sorry there is something wrong on our end. Please try again later."
            reply += "Please note bookings can only be made from tomorrow onwards. :)"
        else:
            return False, "I'm sorry we are all booked! Please check again tomorrow. Thank you for choosing our service!"

        return True, reply       

def cancelBooking(day_of_week, time_of_day, dentist_name, patient_name, date_booking):
    print('in cancelBooking')
    print(day_of_week, time_of_day, dentist_name, patient_name)
    try:
        # TODO: CHange port number if different
        url = 'http://127.0.0.1:8082/timeslot_api/appointments/cancel'
        headers = {'Content-type': 'application/json'}
        data = {
            'time_of_day': time_of_day,
            'day_of_week': day_of_week,
            'dentist_name': dentist_name,
            'patient_name': patient_name,
            'status': True, # False to reserve the spot, True to free it
            'date_appt': date_booking
        }

        print(data)
        response  = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
    except HTTPError as http_err:
        print(response.text)
        print('HTTP error occurred:')  # Python 3.6
        return False, response.text
    except Exception as err:
        print('Other error occurred in requestBooking')  # Python 3.6
        return False, response.text
    else:
        print('Success in cancelBooking!')
        print(response.json())
        resp_obj = json.loads(response.text)
        
        reply = 'Something wrong during cancelling...'
        if resp_obj.get('links'):
            reply = 'This is a confirmation for ' + patient_name +' that booking: \n' 
            reply += 'Next ' +day_of_week + ' '+ date_booking + ' ' + time_of_day
            reply += ' with Dr ' + dentist_name + ' IS CANCELLED! \nThank you for choosing our service :)'
            
        
            
        return True,reply