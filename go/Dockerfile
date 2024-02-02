FROM golang:1.22rc2-alpine3.18

WORKDIR /app

# COPY requirements.txt ./

# RUN pip install -r requirements.txt

COPY . .

CMD ["go", "run", "./main.go"]
