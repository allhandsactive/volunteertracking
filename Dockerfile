FROM python:3.9

COPY . .

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# gunicorn
CMD ["flask",  "db upgrade"]
CMD ["flask", "auto-setup"]
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "run:app"]
