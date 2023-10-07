FROM nginx:1-alpine
COPY ./cf-ips.sh /app/cf-ips.sh
WORKDIR /app

RUN chmod +x cf-ips.sh
RUN bash cf-ips.sh