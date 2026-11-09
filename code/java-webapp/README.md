# java-webapp

Spring Boot web application that exposes the monograph's verification and
simulation pipeline as a REST API plus a server-rendered web UI. It is a
fully independent third implementation of the mathematics (alongside the
Python and Julia stacks): the Klein quartic invariants, spinor phase
enumeration, Dirac eigenvalue, unified formula, hypothesis testing and
LIGO QNM comparison are all recomputed in Java, with plots and multi-format
reports produced server-side.

## What is inside

| Path | Contents |
|------|----------|
| `pom.xml` | Maven build (Spring Boot parent; Java 17). Dependencies: spring-web, Thymeleaf, Validation, Actuator, Jackson, Apache Commons Math, JFreeChart, iText PDF, Apache POI, Lombok, spring-boot-starter-test |
| `src/main/java/com/choptyuk/ChoptyukApplication.java` | Application entry point |
| `.../config/AppConfig.java` | Bean wiring for services |
| `.../model/` | Domain types: `KleinCurve`, `SpinorPhases`, `DiracOperator`, `ChoptyukFormula`, `SurfaceSpec`, `K3Surface`, `KleinCurve`, `TyukovskyEquation`, `EinsteinQNMCorrection`, `QNMEvent`, `HypothesisConfig` |
| `.../service/` | `VerificationService`, `SimulationService`, `PlotService` (JFreeChart, 600 DPI), `ReportService` (PDF via iText, DOCX via POI) |
| `.../controller/` | `WebController`, `VerificationController`, `EnhancedController`, `ReportController` |
| `src/main/resources/application.properties` | All physical parameters (`choptyuk.*`) with defaults; server port 8080; actuator endpoints |
| `src/main/resources/templates/` | Thymeleaf pages: `dashboard.html`, `verify.html`, `simulate.html`, `hypothesis.html`, `reports.html` |
| `src/main/resources/static/` | `css/style.css`, `js/app.js` for the UI |

## How to run

```bash
cd java-webapp
mvn spring-boot:run            # dev run (also used by the docker-compose service)
```

Then open <http://localhost:8080>. The docker-compose service in
`../docker/` runs exactly this command inside a Maven + JDK image with the
source mounted, so no local Maven/JDK installation is required:

```bash
docker compose -f ../docker/docker-compose.yml up java-webapp
```

Standard Maven lifecycle commands (`mvn test`, `mvn package`) work as usual;
the built artifact is a Spring Boot executable JAR.

## Endpoints

Web pages (Thymeleaf):

| Route | Page |
|-------|------|
| `GET /` | Dashboard |
| `GET /verify` | Verification console |
| `GET /simulate` | Simulation sweeps |
| `GET /hypothesis` | Hypothesis testing with custom spinor structures |
| `GET /reports` | Report downloads |

REST API:

| Endpoint | Purpose |
|----------|---------|
| `POST /api/verify` | Run the full verification suite, return JSON results |
| `POST /api/simulate` | Parameter sweeps and convergence data |
| `POST /api/hypothesis` | Test a custom hypothesis configuration |
| `GET /api/enhanced/k3` | K3 surface module (b₂ = 22) |
| `GET /api/enhanced/tyukovsky` | Tyukovsky equations (zero free parameters) |
| `GET /api/enhanced/einstein-qnm` | Einstein GR QNM correction data |
| `GET /api/enhanced/verify` | Extended verification suite |
| `GET /api/reports/{format}` | Report in the requested format (`/api/reports/list` enumerates formats) |

## Verification content

As stated in the application class documentation: Klein curve invariant
verification (genus 3, PSL(2,7) order 168); spinor phase enumeration (64
structures from δ_A, δ_B, δ_C); Dirac eigenvalue via the Lichnerowicz
formula; unified formula evaluation (b-C, a-C); LIGO QNM prediction
comparison; multi-format report generation and publication-quality plots.
All parameters can be overridden in `application.properties`
(`choptyuk.delta-a`, `choptyuk.delta-b`, `choptyuk.delta-c`,
`choptyuk.lambda1`, `choptyuk.verification-tolerance`, `choptyuk.sweep-points`,
plot and report directories, etc.).

## Notes

- Toolchain: Java 17 (enforced by `pom.xml`); build via Maven wrapper-free
  `mvn` commands or the containerised Maven image above.
- Reference values checked by `VerificationService` match the Python and
  Julia stacks: Δ_bC = 3.438710, Δ_Ch base = 3.437883, Δ_Ch full = 3.447040,
  b_Ch = 0.376510, tolerance default 0.0001.
- Plot output goes to `plots/`, reports to `reports/` (configurable); both
  are created on demand at runtime.
- Actuator exposes `health`, `info`, `metrics` with full health details for
  monitoring long verification runs.
