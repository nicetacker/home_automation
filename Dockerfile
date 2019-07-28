FROM golang:1.12.7 as builder

WORKDIR /go/src/github.com/nicetacker/home_automation

# setup
RUN go get -u github.com/golang/dep/cmd/dep 
COPY Gopkg.toml Gopkg.lock ./
RUN dep ensure -vendor-only=true

# build
COPY . .
RUN GOOS=linux GOARCH=arm GOARM=7 CGO_ENABLED=0 go build -o home_automation
#RUN go build -o /app/home_automation

WORKDIR /app

# run
FROM alpine:latest
RUN apk add --no-cache ca-certificates

WORKDIR /app
COPY --from=builder /go/src/github.com/nicetacker/home_automation/home_automation .

# run
CMD ["/bin/sh", "-c", "./home_automation"]

