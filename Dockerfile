FROM python:3.12
RUN mkdir /app
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
COPY core/.env /app/.env
ENV ENV_FILE_PATH /app/.env
CMD ["uvicorn", "core.fastapi_app.app:app", "--host", "0.0.0.0", "--port", "8000"]