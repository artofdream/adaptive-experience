#!/bin/sh
# Push linux/amd64 + linux/arm64 manifest lists to Path B ECR (#416).
# GitLab SaaS / laptop `docker build` + `docker push` emits a single-arch
# manifest (live aea-pilot images were amd64-only). Do not terraform-apply
# ARM64 task defs until `imagetools inspect` shows both platforms on :latest.
set -eu

AEA_PLATFORMS="${AEA_PLATFORMS:-linux/amd64,linux/arm64}"
AEA_BUILDX_BUILDER="${AEA_BUILDX_BUILDER:-aea-multiarch}"
# Official Grafana 10.4.0 tag publishes amd64+arm64. The #331 pin in
# Dockerfile.grafana / compose is the amd64 image GitLab pulled — it cannot
# be the FROM for an arm64 ECR layer. CI overrides AEA_GRAFANA_BASE.
AEA_GRAFANA_BASE="${AEA_GRAFANA_BASE:-grafana/grafana:10.4.0}"

usage() {
  echo "usage: $0 setup|shop|agent-runner|require-platforms <ref>|materialize-from <src> <from> <dest>" >&2
  exit 2
}

require_env() {
  name=$1
  eval "value=\${$name:-}"
  if [ -z "$value" ]; then
    echo "FAIL: $name is required" >&2
    exit 1
  fi
}

grafana_ecr_url() {
  if [ -n "${AEA_ECR_GRAFANA:-}" ]; then
    printf '%s\n' "$AEA_ECR_GRAFANA"
    return 0
  fi
  case "${AEA_ECR_GATEWAY:-}" in
    */gateway)
      printf '%s\n' "${AEA_ECR_GATEWAY%/gateway}/grafana"
      ;;
    *)
      echo "FAIL: set AEA_ECR_GRAFANA or AEA_ECR_GATEWAY ending in /gateway" >&2
      exit 1
      ;;
  esac
}

has_platform() {
  inspect=$1
  platform=$2
  printf '%s\n' "$inspect" | grep -q "$platform"
}

require_platforms() {
  ref=$1
  echo "inspect: $ref"
  inspect=$(docker buildx imagetools inspect "$ref")
  printf '%s\n' "$inspect"
  has_platform "$inspect" 'linux/amd64' || {
    echo "FAIL: $ref has no linux/amd64" >&2
    exit 1
  }
  has_platform "$inspect" 'linux/arm64' || {
    echo "FAIL: $ref has no linux/arm64 (do not pin a single-arch digest for Path B multi-arch)" >&2
    exit 1
  }
}

# Prefer the #331 pin when it is already an index. If GitLab recorded a
# platform digest, fall back to the same tag so this job can still emit
# a dual-arch ECR list. Do not rewrite committed pins from CI.
resolve_from() {
  pinned=$1
  tag=${pinned%%@*}
  echo "inspect: $pinned"
  if inspect=$(docker buildx imagetools inspect "$pinned" 2>/dev/null); then
    printf '%s\n' "$inspect"
    if has_platform "$inspect" 'linux/amd64' && has_platform "$inspect" 'linux/arm64'; then
      printf '%s\n' "$pinned" > /tmp/aea-from-ref
      return 0
    fi
    echo "WARN: $pinned is not a dual-arch index; using $tag for this ECR push (#416)" >&2
  else
    echo "WARN: cannot inspect $pinned; using $tag for this ECR push (#416)" >&2
  fi
  require_platforms "$tag"
  printf '%s\n' "$tag" > /tmp/aea-from-ref
}

materialize_from() {
  src=$1
  from_ref=$2
  dest=$3
  awk -v ref="$from_ref" '
    BEGIN { done = 0 }
    /^[[:space:]]*FROM[[:space:]]+/ && done == 0 && $0 !~ /\$/ {
      print "FROM " ref
      done = 1
      next
    }
    { print }
  ' "$src" > "$dest"
}

setup_buildx() {
  docker info
  # Register QEMU on privileged dind so the amd64 GitLab runner can emit arm64.
  docker run --privileged --rm tonistiigi/binfmt --install amd64,arm64
  if docker buildx inspect "$AEA_BUILDX_BUILDER" >/dev/null 2>&1; then
    docker buildx use "$AEA_BUILDX_BUILDER"
  else
    docker buildx create --name "$AEA_BUILDX_BUILDER" --driver docker-container --use
  fi
  docker buildx inspect --bootstrap
}

push_image() {
  dockerfile=$1
  context=$2
  image=$3
  shift 3
  require_env CI_COMMIT_SHA
  echo "buildx push $image platforms=$AEA_PLATFORMS file=$dockerfile"
  docker buildx build \
    --platform "$AEA_PLATFORMS" \
    --provenance=false \
    --sbom=false \
    -f "$dockerfile" \
    -t "$image:$CI_COMMIT_SHA" \
    -t "$image:latest" \
    --push \
    "$@" \
    "$context"
}

push_from_pin() {
  dockerfile=$1
  context=$2
  image=$3
  pinned=$4
  resolve_from "$pinned"
  from_ref=$(cat /tmp/aea-from-ref)
  workdir=$(mktemp -d)
  materialized="$workdir/Dockerfile"
  materialize_from "$dockerfile" "$from_ref" "$materialized"
  push_image "$materialized" "$context" "$image"
  rm -rf "$workdir"
}

cmd_shop() {
  require_env AEA_ECR_ORCHESTRATION
  require_env AEA_ECR_BFF
  require_env AEA_ECR_GATEWAY
  grafana=$(grafana_ecr_url)
  setup_buildx
  require_platforms "$AEA_GRAFANA_BASE"
  push_from_pin platform/Dockerfile.orchestration . "$AEA_ECR_ORCHESTRATION" \
    "python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254"
  push_from_pin edge/bff/Dockerfile edge "$AEA_ECR_BFF" \
    "python:3.12-alpine@sha256:b64631e04e4920160c50fbe8d8df828f7f35f06f425cb44aa09bca53e708a35a"
  push_from_pin edge/gateway/Dockerfile edge/gateway "$AEA_ECR_GATEWAY" \
    "nginx:1.27-alpine@sha256:65645c7bb6a0661892a8b03b89d0743208a18dd2f3f17a54ef4b76fb8e2f2a10"
  push_image platform/docker/Dockerfile.grafana . "$grafana" --build-arg "AEA_GRAFANA_BASE=$AEA_GRAFANA_BASE"
}

cmd_agent() {
  require_env AEA_ECR_AGENT_RUNNER
  setup_buildx
  push_from_pin platform/docker/Dockerfile.agent-runner . "$AEA_ECR_AGENT_RUNNER" \
    "python:3.12-slim@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea"
}

case "${1:-}" in
  setup) setup_buildx ;;
  shop) cmd_shop ;;
  agent-runner) cmd_agent ;;
  require-platforms)
    [ -n "${2:-}" ] || usage
    require_platforms "$2"
    ;;
  materialize-from)
    [ -n "${2:-}" ] && [ -n "${3:-}" ] && [ -n "${4:-}" ] || usage
    materialize_from "$2" "$3" "$4"
    ;;
  *) usage ;;
esac
