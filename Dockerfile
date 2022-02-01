FROM python:3.8-slim-buster
WORKDIR /home
RUN apt-get update && apt-get install -y build-essential
RUN mkdir /home/data
COPY . /home/app/
COPY .env requirements.txt /home/
RUN pip install -r requirements.txt
RUN python app/manage.py collectstatic --no-input

CMD python app/manage.py runserver