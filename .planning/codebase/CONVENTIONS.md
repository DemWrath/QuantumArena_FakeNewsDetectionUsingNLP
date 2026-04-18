# Code Conventions

## Code Style & Modularity

### Python Implementations
- **Encapsulation**: Historically, imported scripts inside `Fake_News_Detection` fired side effects iteratively inside the global execution scope (e.g. performing file system reads immediately on `import`).
- **Modernized Standard**: We are currently migrating every procedural action into explicit definition blocks (`def ...`) wrapped with standard entrypoint hooks (`if __name__ == "__main__":`).
- **Dependencies**: Explicit requirement locking is maintained. We execute relative pathing calculations via `os.path.dirname(os.path.abspath(__file__))` to prevent pipeline failures triggered exclusively by changes in `cwd`.

### Next.js Implementations (HonestyMeter)
- Utilizes functional components mapped across React hooks.
- Leverages typical JS Promise handling constraints against async backend endpoints.

## Error Handling
- Machine Learning pipelines implement explicit error intercepts to fail gracefully if serialized cached objects (`.joblib`) vanish.
- The `pipeline.py` json generator will wrap model evaluations in blocks guaranteeing at least stubbed JSON output (`{error: "detailed message"}`) instead of propagating raw crash dumps dynamically to the web layer.
