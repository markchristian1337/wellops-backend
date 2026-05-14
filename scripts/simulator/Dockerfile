FROM python:3.13.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "scripts.simulator.simulate_sensors"]