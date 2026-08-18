# Framework Source → Project Runtime → Release

Human-only explanatory view. The release builder and workflow remain executable sources of truth.

```mermaid
flowchart TD
    S["Framework Source\nrepository"] --> Q["contracts + audits + tests"]
    Q --> B["tools/build_release.py"]
    B --> R["Project Runtime ZIP"]
    B --> M["manifest.json"]
    B --> H["SHA256SUMS.txt"]
    R --> G["GitHub Release"]
    M --> G
    H --> G

    V["docs/human + docs/visuals"] -. "source-only; excluded" .-> X["not packaged"]
```

Project Runtime is generated from Framework Source rather than maintained as a second independent kit. Human documentation can grow without increasing the runtime footprint.
