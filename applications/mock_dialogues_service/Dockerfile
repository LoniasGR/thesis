FROM python:3.10

WORKDIR /code/app

COPY app/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY app /code/app/
COPY ./frontend/dist /code/app/frontend/dist

HEALTHCHECK --interval=1m --timeout=3s \
    CMD curl -f http://localhost/health || exit 1
EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
