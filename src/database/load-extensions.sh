#!/bin/sh

# Install necessary build tools and libraries
apt-get update && apt-get install -y build-essential git postgresql-server-dev-all

# Clone the pg_similarity repository
git clone https://github.com/eulerto/pg_similarity.git /usr/src/pg_similarity

# Build and install pg_similarity extension
cd /usr/src/pg_similarity && make && make install

# Clean up build dependencies
apt-get remove -y build-essential git postgresql-server-dev-all && apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/* /usr/src/pg_similarity

psql postgres://nekosauce:nekosauce@localhost:5432/nekosauce -v ON_ERROR_STOP=1 <<EOF
create extension pg_similarity;
select * FROM pg_extension;
EOF

exec "$@"