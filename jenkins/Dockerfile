FROM jenkins/jenkins:lts
USER root

RUN apt-get update && apt-get install -y curl tar python3 docker.io

RUN curl -sSL https://sdk.cloud.google.com | bash -s -- --disable-prompts --install-dir=/opt

ENV PATH="/opt/google-cloud-sdk/bin:${PATH}"

RUN gcloud components install gke-gke-auth-plugin --quiet

RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-4 | bash

USER jenkins