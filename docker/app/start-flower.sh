
#!/bin/sh

set -o errexit
set -o nounset

celery flower -A testfighters.apps.taskapp --basic_auth="${CELERY_FLOWER_USER}:${CELERY_FLOWER_PASSWORD}"
