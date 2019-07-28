FROM golang:1.12.7-alpine3.10

COPY . /go/src/home_automation

WORKDIR /go/src/home_automation

RUN apk update \
  && apk add --no-cache git \
  && go get -u github.com/golang/dep/cmd/dep \
  && dep ensure

CMD ["go", "main.go"]

