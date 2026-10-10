# multilang/ — the bridge in six languages

Standalone self-test twins of the closed-form core (constants,
correction quanta, contacts, Wu residual, Gascheau growth, the
committed gap-law sample).  Each prints the same validation block and
exits.  Nothing is downloaded, nothing is fitted, nothing is hidden.

| language | status at packaging |
|---|---|
| JavaScript (`node javascript/bridge.mjs`) | verified, **14/14 PASS** |
| C (`gcc -O2 -o bridge c/bridge.c -lm`) | verified, **14/14 PASS** |
| C++ (`g++ -O2 -std=c++17`) | verified, **14/14 PASS** |
| Go (`go run go/bridge.go`) | source twin |
| Rust (`rustc -O rust/bridge.rs`) | source twin |
| Julia (`julia julia/bridge.jl`) | source twin |

`reference_output.txt` — the committed outputs of the verified twins.
