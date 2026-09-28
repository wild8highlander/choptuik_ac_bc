# docker

Container definitions for reproducing the repository's verification runs and
for launching the two web front-ends without installing any toolchain
locally. The image is built for reproducibility: fixed base image, pinned
system libraries, and a default command that runs the full Python
verification non-interactively.

## What is inside

| File | Contents |
|------|----------|
| `Dockerfile` | Single-stage image on `python:3.12-slim`. Installs `gcc`, `g++`, `gfortran`, OpenBLAS/LAPACK, then `python/requirements.txt` plus `python-docx reportlab markdown jinja2` for the multi-format report writers. Copies `python/` into `/app`. Default command: `python /app/python/run.py --mode verify --non-interactive --output-dir /app/output` |
| `docker-compose.yml` | Three services: `python-verify` (builds the image, mounts `../output`), `interactive-viz` (Node image, mounts `../interactive-viz`, port 3000), `java-webapp` (Maven + JDK image, mounts `../java-webapp`, port 8080). Named volumes cache `node_modules` and the Maven repository |

## How to run

Build and run the headless verification (context must be the repository root,
because the Dockerfile copies `python/`):

```bash
docker build -f docker/Dockerfile -t choptyuk-verify .
docker run choptyuk-verify
```

Or use Compose for all three services:

```bash
docker compose -f docker/docker-compose.yml run --rm python-verify   # one-shot verification
docker compose -f docker/docker-compose.yml up interactive-viz       # Next.js UI on :3000
docker compose -f docker/docker-compose.yml up java-webapp           # Spring Boot UI on :8080
```

Verification artifacts land in `output/` at the repository root thanks to the
`../output:/app/output` mount; open `output/logs/execution.log` and the
generated report files after the container exits.

## What a verification run produces

The default command (`run.py --mode verify --non-interactive`) fills
`output/` with the same artifacts as a bare-metal run of the Python stack:

| Artifact | Location |
|----------|----------|
| Execution log | `output/logs/execution.log` |
| Verification results | `output/` (JSON results of the full suite) |
| Simulation sweeps and plots | `output/plots/` |
| Multi-format reports | `output/reports/` (DOCX, PDF, TXT, MD, CSV, HTML, JSON) |

## Compose service reference

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `python-verify` | built from `docker/Dockerfile` | — | one-shot full verification, artifacts mounted to `../output` |
| `interactive-viz` | `node:20-slim` | 3000 | Next.js dashboard dev server (`npm install && npm run dev`) |
| `java-webapp` | `maven:3.9-eclipse-temurin-17` | 8080 | Spring Boot stack (`mvn spring-boot:run`) |

## Notes

- The image is intentionally minimal: no Julia and no Node inside the Python
  image — the Compose file pulls separate language images for the web apps
  instead of baking a monolithic container.
- `interactive-viz` and `java-webapp` services mount the source directories
  live, so edits on the host are picked up by their dev servers without a
  rebuild.
- The container writes only under `/app/output`; results are deterministic
  and should match a bare-metal run of `python run.py --mode verify
  --non-interactive` from `python/`.
