FROM python:3.10
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x ./migrations.sh
CMD ["./migrations.sh"]
