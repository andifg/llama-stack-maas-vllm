# LLAMA STACK MAAS DEMO 

## Prerequesites

- direnv
- uv


## Rebuild & Run Distro / Llama stack server 

0. Install dependencies & activate venv

```bash
uv venv      
source .venv/bin/activate
uv sync   
```


1. Build llama stack distribution (Only needed if new dependencies are needed in image)

```bash
CONTAINER_BINARY=podman llama stack build --config maas-remote-stack/llamastack-m-build.yaml --image-name maas-remote-stack
```


2. Run llama stack image 

BE CAREFUL: Image tag can differ ! 

Load environment variables
```bash
direnv allow
```

```bash
podman run \
  --name maas-remote-stack \
  -p 8321:8321 \
  -e VLLM_URL=$VLLM_URL \
  -e VLLM_API_TOKEN=$VLLM_API_TOKEN \
  localhost/maas-remote-stack:0.2.18
```


## Run prebuild distro 

```bash
cd maas-remote-stack 
podman compose up
```


## Run llama stack client 

```bash
uv run python3 main.py
```