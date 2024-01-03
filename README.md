# Project Title
## Todos App

# Project Description
- This Todos App is a simple yet powerful task management application designed to help users organize their daily activities efficiently.
-  With an intuitive user interface(Swagger UI from FastAPI) and essential features, it simplifies the process of creating, tracking, and completing tasks.

# Features
- User can create their account, get token & the use this token to create their tasks.
- Has advanced verification method to secure user' tasks and their account.
- If token is invalid, it will not allow any user to create tasks.
- Easily add new tasks.
- Mark tasks as completed to track your progress.
- Remove tasks that are no longer relevant or needed.

# Screenshot
![Todos App](https://github.com/amitsahni97/todos-app/assets/75803822/808102f7-8d17-49e8-ab4a-74958989d59a)


# Installation
- Clone the repository: git clone https://github.com/amitsahni97/todo-app.git
- Create a new virtual environment using terminal(run python -m venv venv_name)
- In terminal, run pip install -r requirements.txt (this will install all the dependencies needed to run this project)
- In terminal, run uvicron main:app --reload
- See the port number on which the server is running in terminal
- Now type localhost:port_numer/docs. This will oopen Swagger UI(Interface) to interact with this app
- Great!, now you can create account, get token & then start creating your tasks by using token
