# Build: docker build -t wxwmatt/autoscaler_test:1.0 .
# Run: docker run -p 12112:2112 wxwmatt/autoscaler_test:1.0

FROM golang:latest AS build
COPY . /src/
WORKDIR /src/
RUN CGO_ENABLED=0 go build -o autoscaler_test

# For development
FROM alpine:latest
# For deployment
# FROM scratch
WORKDIR /app
COPY --from=build /src/autoscaler_test /app/
EXPOSE 8080
ENTRYPOINT ["./autoscaler_test"]
