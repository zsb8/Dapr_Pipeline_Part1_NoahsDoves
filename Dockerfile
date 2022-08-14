FROM python:3.8-slim-buster
WORKDIR /usr/src/app
COPY ./requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
COPY ./default_scrapyd.conf /usr/local/lib/python3.8/site-packages/scrapyd/
# CMD [ "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "80" ]
CMD [ "scrapyd"]


