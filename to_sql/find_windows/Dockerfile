FROM ubuntu:latest

RUN apt-get update && apt-get -y install -qq --force-yes cron

WORKDIR /cron

COPY find-window-cron /etc/cron.d/find-window-cron
COPY find_gaps_and_windows.sql /src/find_gaps_and_windows.sql
COPY create_env_load_file.sh /src/create_env_load_file.sh

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/find-window-cron

# Apply cron job
RUN crontab /etc/cron.d/find-window-cron

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run the command on container startup
RUN apt-get install -y postgresql-client

# Env load script
RUN chmod 777 /src/create_env_load_file.sh

CMD /src/create_env_load_file.sh && cron && tail -f /var/log/cron.log

