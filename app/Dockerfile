FROM python:3.7

RUN apt-get update && apt-get install -y python3-dev supervisor nginx \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /hw1

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY static /usr/share/nginx/html/static
COPY __init__.py /app/
COPY routes.py  /app/
COPY setting /app/setting
COPY tests /app/tests
COPY nginx.conf /etc/nginx/nginx.conf
COPY uwsgi.ini /etc/uwsgi/uwsgi.ini
COPY supervisord.ini /etc/supervisor/conf.d/supervisord.ini

WORKDIR /app
RUN mkdir /app/upload_folder

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.ini"]
