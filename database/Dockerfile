FROM postgres:alpine

# Install necessary build tools and libraries
RUN apk update \
    && apk add --no-cache build-base git postgresql-dev clang15 llvm15

# Clone the pg_similarity repository
RUN git clone https://github.com/eulerto/pg_similarity.git /usr/src/pg_similarity

# Build and install pg_similarity extension
RUN cd /usr/src/pg_similarity \
    && make \
    && make install

# Clean up build dependencies
RUN apk del build-base git clang \
    && rm -rf /usr/src/pg_similarity

EXPOSE 5432