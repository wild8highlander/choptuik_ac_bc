# Contributing to Spinor Corrections b-C & a-C

**Author:** Ishak Khamzatovich Isaev (Исаев Исхак Хамзатович)
**Email:** aslan08_05@mail.ru
**GitHub:** https://github.com/wild8highlander
**Repository:** https://github.com/wild8highlander/choptuik_ac_bc

Thank you for your interest in contributing to this project! This document provides guidelines for contributions.

## How to Contribute

### Reporting Issues
- Use the GitHub Issue templates in `.github/ISSUE_TEMPLATE/`
- Include your computational environment (Python/Julia/Java version, OS)
- For verification discrepancies, include the full execution log

### Submitting Changes
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes with appropriate tests
4. Run the test suite: `pytest python/tests/` (Python), `Pkg.test()` (Julia)
5. Submit a Pull Request with a clear description

### Code Standards

**Python:**
- Follow PEP 8 with line length 120
- Type hints required for all public functions
- Docstrings in NumPy style
- Minimum test coverage: 80%

**Julia:**
- Follow Julia style guide
- Docstrings for all exported functions
- Unit tests in `test/` directory

**Java:**
- Google Java Format
- Javadoc for all public methods
- JUnit 5 tests

**TypeScript/React:**
- ESLint + Prettier
- Component tests with React Testing Library

### Verification Standards

Any change to core mathematical computations MUST:
1. Not change verified results by more than numerical precision (ε < 10⁻¹⁰)
2. Include a comparison against the reference values in `docs/monograph/original_verification_results.json`
3. Pass all existing verification tests
4. Include updated execution logs

### Adding New Features
- New spinor structures or group configurations are welcome
- New surface types (beyond Klein, Bolza, Bring, Macbeath) should follow the existing `SurfaceSpec` pattern
- New report formats should implement the `ReportWriter` interface/protocol
- New visualization types should be added to the `visualization/` module

## Code of Conduct

All contributions become the intellectual property of Ishak Khamzatovich Isaev under the Isaev Proprietary License. By submitting a contribution, you agree that the Author retains all rights as specified in the LICENSE file.
