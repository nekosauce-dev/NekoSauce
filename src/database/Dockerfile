FROM postgres:alpine

# Install necessary build tools and libraries
RUN apk update \
    && apk add --no-cache build-base git postgresql-dev clang15 llvm15

RUN /bin/sh -c "load-extensions.sh"

EXPOSE 5432