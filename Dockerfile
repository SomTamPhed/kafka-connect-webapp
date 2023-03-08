FROM python:3.10
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

ENV SECRET_KEY "fdkjshfhjsdfdskfdsfdcbsjdkfdsdf"
ENV DEBUG "True"
ENV APP_SETTINGS "config.DevelopmentConfig"
ENV DATABASE_URL "sqlite:///db.sqlite"
ENV FLASK_APP "src"
ENV FLASK_DEBUG "1"
ENV FLASK_RUN_PORT "8000"
ENV FLASK_RUN_HOST "0.0.0.0"
COPY . /code
CMD ["/bin/bash", "/code/docker-entrypoint.sh"]

# docker build -t flask_webapp .
# docker run -d -p 5000:5000 flask_webapp
