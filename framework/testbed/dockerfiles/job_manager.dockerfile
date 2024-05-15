# syntax=docker/dockerfile:1
FROM dcastro93/alpine_base:1.0

COPY ./onion_pages.tzst /decompress_onion_pages

RUN \
  apk add --update \
    openssh-client \
    rsync \
    ansible \
    tar \
    zstd
    
RUN python3 -m pip install --upgrade pip \
  && python3 -m pip install \
    docker \
    docker-compose \
  && python3 -m pip cache purge
### TODO: cannot install numpy

ADD ./job_manager.sh /job_manager.sh
ADD ./job_manager_screen.sh /job_manager_screen.sh

RUN chmod +x /job_manager.sh
RUN chmod +x /job_manager_screen.sh

ENTRYPOINT [ "/job_manager.sh" ]
