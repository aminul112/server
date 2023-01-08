# Server Async project

Building instruction for macOS. In Linux, it should be very similar.
If you want to modify ip, port, db config changes or anything feel free to change .env file. If you do not have
any values defined in .env file, there will be some default values in the main.py file.

** Note: you should update docker-compose.yml file accordingly including database section. 


## Setup

### Poetry

Make Python virtual environment inside project directory:

    poetry config virtualenvs.in-project true

Install dependencies:

    poetry install

#### Activate the virtual environment

    source .venv/bin/activate


## Building
Make sure Docker is installed and running

### Build docker
    
    docker-compose build 


## Running

### Run docker
Start the image:

    docker-compose up

You can see logs in the console. Log is also saved in the log directory.
