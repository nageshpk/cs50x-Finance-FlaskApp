# cs50x-Finance-FlaskApp

- This is not the official submission of the CS50X Finanace problem set.
- This is a different version which is developed on local machine.

- You do not need to import SQL module from CS50.

![image](https://user-images.githubusercontent.com/38485662/199548453-f183d633-5616-4539-87af-9229c5fcd7ae.png)

- Here a sqlite database is created locally for that you need to install [sqlite3](https://www.sqlite.org/download.html) on your machine,
and import the sqlite3 module to run the queries.

#### Screenshots

- ![image](https://user-images.githubusercontent.com/38485662/199657785-b5a9246d-1372-4701-8be0-bb82d7090298.png)


#### To run this on local machine 

##### Create a virtual environement
```
pip install virtualenv
virtualenv <env name>
```
##### Activate the virtual environment and install the required libraries
```
env\scripts\activate
pip install -r requirements.txt
```



##### Clone the repository to local machine
```
git clone <repo url>
cd <folder name>
```

##### In order to run the flask server, update the environment variable FLASK_APP
```
FLASK_APP = app.py
flask run
```

##### Built using

- HTML5, CSS3, Bootstrap
- Python
- Flask web framework, flask session
- sqlite database
