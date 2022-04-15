# Build: docker build -t go/webservice:1.0 .
# Run: docker run -p 12112:2112 go/webservice:1.0

FROM golang:latest AS build
COPY . /src/
WORKDIR /src/
RUN CGO_ENABLED=0 go build -o prometheus_test

#FROM alpine:latest
FROM scratch
WORKDIR /app
COPY --from=build /src/prometheus_test /app/
EXPOSE 2112
ENTRYPOINT ["./prometheus_test"]
