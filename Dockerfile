FROM jjanzic/docker-python3-opencv:contrib

# RUN apt-get update -y
# RUN apt-get install -y python-pip python-dev build-essential
# RUN pip --version
# RUN apt-get install Command.certificates
# RUN pip install --index-url=https://pypi.python.org/simple/ --upgrade pip

COPY . /app
WORKDIR /app/app

RUN pip install -r ../requirements.txt

CMD ["python", "app.py"]
