FROM postgres:alpine

COPY . /src
WORKDIR /src

# Install necessary build tools and libraries
RUN apk update \
    && apk add --no-cache build-base git postgresql-dev clang15 llvm15

RUN /bin/sh -c "/src/load-extensions.sh"

EXPOSE 5432