FROM python:3.9.13

RUN apt -y update && apt -y install libmagic1 cron tzdata sudo vim htop && \
    rm -rf /var/lib/apt/lists/* && \
    apt clean

RUN ln -fs /usr/share/zoneinfo/Asia/Tehran /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

#RUN (crontab -l ; echo "* * * * * cd /app && sudo -u root /usr/local/bin/python3 /app/manage.py dailyplangenerator") | crontab
#RUN (crontab -l ; echo "* * * * * cd /app && sudo -u root /usr/local/bin/python3 /app/manage.py checkplan") | crontab

ARG port=8000
ENV GUNICORN_WORKER_NO=10
ENV GUNICORN_LISTENINIG_PORT=${port}
ENV GUNICORN_TIMEOUT=1900


WORKDIR /app
RUN mkdir media statics
VOLUME [ "/app/media" ]
VOLUME [ "/app/statics" ]
RUN pip3 install --upgrade pip
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .

RUN chmod +x start.sh
EXPOSE ${port}
CMD [ "./start.sh" ]