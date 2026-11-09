FROM python:3
MAINTAINER Miles Gurney "mgurney@uoregon.edu"
RUN apt-get update -y
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["flask_brevets.py"]
