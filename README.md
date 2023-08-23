# NekoSauce
An anime art source finder.

## Stack

The project is small but uses a bunch of different tools to handle different things.

- **Database**: PostgreSQL
- **Backend (API)**: Django.
- **Frontend**: Next.js + TailwindCSS
- **Message Broker**: RabbitMQ (used together with celery to update the database with new sauces)
- **Cache**: Redis (Rate limits, general caching)

## How does it work

The API runs 3 processes: API workers, Celery workers, and Celery beat.
- **API workers**: Handle API requests. Each of them runs an instance of the API.
- **Celery workers**: Handle background tasks. The two main background tasks fetch and update sauces from sources, and hash images.
- **Celery beat**: Background tasks scheduler. Works like Cron, but it's handled from the API admin site. It sends the `updatesauces` and `updatehashes` tasks to the celery workers.

