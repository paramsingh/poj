# poj

POJ is an online judge. I couldn't think of a better name.

## Setup

Clone the repository

    git clone https://github.com/paramsingh/poj.git

cd into the cloned directory and setup a new virtualenv there

    cd poj/
    virtualenv .

Activate the newly created virtualenv and install all the required dependencies in it using pip

    source bin/activate
    pip install -r requirements.txt

Install docker for your distribution and create an image named 'poj' using the dockerfile in 'poj/docker'

    cd docker
    docker build -t poj .

Create a new database.

    python manage.py migrate

Create an admin user

    python manage.py createsuperuser

Run the development server, the redis server, the celery worker and scheduler, each in a different terminal.

    python manage.py runserver
    redis-server
    celery -A poj worker -l info
    celery -A poj beat -l info

The site should be accessible at `localhost:8000/judge`

