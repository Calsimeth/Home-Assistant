# Agent Instructions

- Do not read standard Home Assistant files that commonly contain sensitive credentials or secrets.
- Treat files such as `secrets.yaml`, `.storage/*`, credential/token/key files, and any user-specific Home Assistant config containing passwords, tokens, API keys, or private URLs as off-limits unless the user explicitly asks for that specific file to be inspected.
- If a task appears to require one of these files, ask the user for guidance or for a redacted excerpt instead of opening the file directly.
