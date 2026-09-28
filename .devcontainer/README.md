# .devcontainer

Development-container configuration that provisions a complete toolchain for
all four implementations of the repository (Python, Julia, Java, Node) in one
reproducible environment. Opening the repository in a Devcontainer-compatible
editor ("Reopen in Container") installs every runtime the verification
suites need, together with the recommended extensions.

## What is inside

| File | Contents |
|------|----------|
| `devcontainer.json` | Base image `mcr.microsoft.com/devcontainers/base:ubuntu-22.04` with four features: Python 3.12 (with JupyterLab), Julia 1.10, Java 17, Node 20. Post-create hooks install each stack's dependencies; VS Code customisations add Python/Jupyter/Julia/Java extensions plus Ruff, Prettier, Biome, Tailwind and markdownlint. Port forwards: 3000 (interactive visualization), 8080 (Java web app), 8888 (Jupyter). Sets `PYTHONPATH` to `python/src` and `JULIA_PROJECT` to `julia/` |

### Toolchain and ports at a glance

| Feature | Toolchain | What it enables |
|---------|-----------|-----------------|
| Python | 3.12 + JupyterLab | `python/` verification suite, `notebooks/` |
| Julia | 1.10 | `julia/` verification suite |
| Java | 17 | `java-webapp/` Spring Boot stack |
| Node | 20 | `interactive-viz/` dashboard |

| Port | Auto-forward | Label |
|------|--------------|-------|
| 3000 | open browser | Interactive Visualization |
| 8080 | open browser | Java Web App |
| 8888 | open browser | Jupyter |

## How to use

1. Open the repository in an editor with Devcontainer support and choose
   **Reopen in Container** (or rebuild the container after pulling changes).
2. The `postCreateCommand` block runs three installs, each tolerant of
   failure so one broken optional stack never blocks the others:
   - Python: `pip install -r python/requirements.txt`
   - Julia: `cd julia && julia --project=. -e 'using Pkg; Pkg.instantiate()'`
   - Node: `cd interactive-viz && npm install`
3. Forwarded ports open automatically:
   - **3000** — `interactive-viz` Next.js dev server
   - **8080** — `java-webapp` Spring Boot server
   - **8888** — Jupyter (for `notebooks/`)
4. Because `PYTHONPATH` and `JULIA_PROJECT` are preset, verification works
   from any shell in the container:
   - `cd python && python run.py --mode verify --non-interactive`
   - `cd julia && julia run.jl --verify`

## Notes

- Feature versions (Python 3.12, Julia 1.10, Java 17, Node 20) are the
  container's toolchain picks; the code itself targets Python ≥ 3.10 and
  Julia ≥ 1.9 (see `python/pyproject.toml` and `julia/Project.toml`).
- The Julia `Pkg.instantiate()` call is silent-failure (`|| true`) because the
  project's registry dependencies (JSON, Plots) download on first run; rerun
  it manually if the Julia tests report missing packages.
- No extra files are created in the repository by the container beyond the
  usual build caches (`.next/`, `target/`, `output/`, `__pycache__/`).
- Recommended editor extensions installed automatically: Python, Jupyter,
  Julia language support, the Java extension pack, Tailwind CSS IntelliSense,
  Prettier, Ruff, Biome and markdownlint — matching the lint/format tools
  configured in the repositories' pre-commit hooks.
- The container needs no credentials; everything it installs comes from the
  public devcontainer feature registry and the language package managers.
