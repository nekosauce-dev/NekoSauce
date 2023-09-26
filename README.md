# NekoSauce

An anime & manga source finder. Written in Django (Python 3) (Backend) and Next.js (Node.js) (Frontend).

[Documentation](https://docs.nekosauce.org/) • [Donate](https://ko-fi.com/Nekidev)

## Stack

The project is small but uses a bunch of different tools to handle different things.

- **Database**: PostgreSQL
- **Backend (API)**: Django
- **Frontend**: Next.js + TailwindCSS
- **Message Broker**: RabbitMQ (used together with dramatiq to update the database with new sauces)
- **Cache**: Redis (Rate limits, general caching)

## Deployment

It's really easy to set up a deployment. Following the steps below will get you up and running in no time.

### Install Docker, Docker Compose, and Git

You need these to get the project's source code and run it. They all can be downloaded from their official websites.

### Clone the project

Clone this repository using the `git` command:

```bash
git clone https://github.com/nekosauce-dev/NekoSauce.git
```

### Set up the project

Enter the project directory (`cd NekoSauce`). It'll be easier to follow the next steps if you open it on your IDE to modify the configuration files.

1. Rename `compose.yml` (if you want to run it in production) or `compose.dev.yml` (to run it locally) to `docker-compose.yml`.
2. Rename `/.env.example` to `/.env`. This file will contain all your settings for the project. After doing this, check it out and set up all environment variables to your own values. They're all documented, so you shouldn't have any issues with that. There are a few of them that have default values; You shouldn't need to modify them unless you're making some heavier modifications that are not documented here.
3. Rename `/secrets.example/` to `/secrets/`. This folder contains a few sensitive values that are transported using [Docker secrets](https://docs.docker.com/engine/swarm/secrets/). None of these values should be shared with anyone. The file names are pretty self-explaining, but anyway here it's what each of them means and what they should contain:
    - `./secrets/BACKEND_SECRET_KEY.txt`: Django's secret key. You can generate one using `LC_CTYPE=C tr -dc '[:print:]' < /dev/urandom | head -c 50`. You can learn more about this secret key and what it's used for [in the Django documentation](https://docs.djangoproject.com/en/4.2/topics/signing/). It should be at least 50 characters long, and kept secure.
    - `./secrets/DATABASE_PASSWORD.txt`: PostgreSQL's password. Basically, the database's password.
    - `./secrets/NGINX_CERT_CERTIFICATE.pem`: The SSL certificate for Nginx. You can generate one using OpenSSL or from Cloudflare if you're using it for your domain.
    - `./secrets/NGINX_CERT_PRIVATE_KEY.pem`: The SSL private key for Nginx. You can generate one using OpenSSL or from Cloudflare if you're using it for your domain.

### Build and run

If everything was set up correctly, the next commands should run without any issues:

```bash	
# Build the project with the current settings
docker compose build

# Start NekoSauce
docker compose up
```

It'll finish setting up the last things (nothing you should worry about) and start the web server at `localhost:443` in case of the production compose file, or at `localhost:80` in case of the development compose file.

If everything is running correctly and you cannot detect any issues, you're good to go. Stop the server pressing `Ctrl + C` and restart it in the background using `docker compose up -d`.

### Adding some database records

Paste the following in your terminal:

```bash
docker exec -it nekosauce-backend-1 python manage.py createsuperuser
```

You'll be asked to create a new user, which you'll use to access the administration site. This user will have access to ALL THE SITE'S DATA, so make sure to give its credentials wisely. Better if you keep them yourself.

Go to the administration site at `https://mydomain.uwu/admin/`. You'll need to log in using the credentials of the super user you created in the last step. Once you do so, you'll be able to access the administration site.

You'll see that everything is empty, except for the "users" table where you'll only be able to see yourself. Go to `/admin/sauces/source/`, which will be empty. To enable a source, you need to create it (otherwise, you won't be able to fetch sauces from that source). Sources are internally identified by their name (despite them having a numeric ID). For example, to enable Danbooru, you must create a new source named `Danbooru` (case insensitive, but check for typos or it won't be detected).

The currently available sources are:
- Danbooru
- Gelbooru

### Setting up cron jobs

Now that you have the server correctly set up, you just need to set up cron jobs to update the database with new sauces/hashes/thumbnails/etc. There are 3 commands you need to set up:

- `docker exec nekosauce-backend-1 python manage.py updatesauces`: Will fetch new sauces from all sources, or from one source if passed as an argument.
- `docker exec nekosauce-backend-1 python manage.py updatehashes`: Will download the fetched sauces (the file) from their source's CDN or however they serve their images and calculate their hash.
- `docker exec nekosauce-backend-1 python manage.py updatethumbs`: Will download the fetched images from their source's CDN or however they serve their images and update the thumbnails and their sha512 hash.

You can get more info about them adding `--help` at the end of each command. It's up to you to decide how frequently each of them will run, but you should do some benchmarking to see what works best for you.

Ideally, each of them shouldn't be running twice at the same time nor not be running at all unless it has finished it's work and there isn't anymore to do. In other words, don't have them overlapping themselves since it'll reduce their efficiency.

Notice that the command itself may finish in a few seconds/minutes, but `updatehashes` and `updatethumbs` actually spawn background tasks in the Dramatiq workers. These commands shouldn't be rerun until the background tasks are finished. Running it again will cause duplicate tasks to be spawned, resulting in a waste of time and server resources.