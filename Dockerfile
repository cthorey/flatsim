FROM python:3.9-slim-buster as base

# Change shell
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
RUN python -m pip install --upgrade pip

# Install dependencies
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt


ENTRYPOINT ["streamlit","run","/workdir/app/app.py"]

