# Use official Python image
FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt


# Run the bot
CMD ["python", "bot.py"]
