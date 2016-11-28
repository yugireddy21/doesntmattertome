#!/bin/sh
# Run to create a docker image

IMAGE_REPO=doesntmattertome
IMAGE_NAME=phase0
IMAGE_TAG=latest

if [ ! -z "$IMAGE_REPO" ]; then
  FULL_IMAGE=${IMAGE_REPO}/
fi
FULL_IMAGE=${FULL_IMAGE}${IMAGE_NAME}
if [ ! -z "$IMAGE_TAG" ]; then
  FULL_IMAGE=${FULL_IMAGE}:${IMAGE_TAG}
fi

# Get the latest commit sha for the code
GIT_SHA=`git rev-parse HEAD`
GIT_BRANCH=`git rev-parse --abbrev-ref HEAD`

docker build . \
  --build-arg git_sha=$GIT_SHA \
  --build-arg git_branch=$GIT_BRANCH \
  --build-arg service_name=$IMAGE_NAME \
  -t $FULL_IMAGE
