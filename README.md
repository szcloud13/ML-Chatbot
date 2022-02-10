Build Instructions:

To start frontend:
1. Ensure current directory is inside the folder [‘dockerized_ass2’]
2. Run command: ​ $ ​ python3 -m http.server
3. Access ​ http://127.0.0.1:8000/​ on browser to access the chat.

To run the chatbot api:​ (Locally according to specifications) ​ (Assume Linux environment)
1. Enter directory [‘dockerized_ass2/chatbot’]
2. Create virtual environment for the flask app:
$​ python3 -m venv myenv
$​ source myenv/bin/activate
$ ​ pip3 install -r requirements.txt
$​ python3 demo/__init__.py
3. The bot server swagger site can be accessed
http://localhost:8080/static/swagger-ui/index.html#/​ ,
basic greetings should now be understood.

To run the dockerized service for timeslot API:
1. Enter directory [‘dockerized_ass2/timeslots_docker’]
2. Run command: ​ $ ​ sudo docker build -t timeslot_api .
3. $​ docker volume create data
(to enable server to store data inside docker image, create volume named ‘data’, used
mounting)
4. Initiating and run the docker: ​ $ ​ sudo docker run -it --name=timeslot_api --mount source=data,destination=/service/demo -p 8082:5000 timeslot_api

● After quitting, the container can be still be run using the commands below such that all post request data for booking are retained for this specific docker image:

5. To start server:​ $​ sudo docker start timeslot_api
6. To stop server: ​ $ ​ sudo docker stop timeslot_api
7. Access http://localhost:8082/static/swagger-ui/index.html#/​ to test the URIs

To run dockerized service for dentists
1. Enter directory [‘dockerized_ass2/dentists_docker’]
2. Run command:
$​ sudo docker build -t dentist_api .
$​ sudo docker run -p 8081:5000 -t dentist_api
3. Access ​ http://localhost:8081/static/swagger-ui/index.html#/​ to test the URIs
