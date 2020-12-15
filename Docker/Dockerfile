FROM python:3.8
WORKDIR /functions
COPY requirements.txt /
RUN apt update && apt install libgdal-dev --yes && apt install python3-dev --yes
RUN pip install -r /requirements.txt
COPY ./ ./
EXPOSE 5000
CMD ["python", "./app.py"]
