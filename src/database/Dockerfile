FROM postgres:latest

# Install necessary build tools and libraries
RUN apt update && apt upgrade -y \
    && apt install git make gcc postgresql-16 postgresql-server-dev-16 -y

# Clone the pg_similarity repository
RUN git clone https://github.com/eulerto/pg_similarity.git /usr/src/pg_similarity

# Build and install pg_similarity extension
RUN cd /usr/src/pg_similarity \
    && make \
    && make install

# Clean up build dependencies
RUN apt remove git -y \
    && rm -rf /usr/src/pg_similarity

EXPOSE 5432