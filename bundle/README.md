# Secoda Analysis MCP — Desktop Bundle

This directory contains everything needed to build a `.mcpb` bundle for one-click installation in Claude Desktop.

## Structure

```
bundle/
├── manifest.template.json   # Public template — tracked in git
├── manifest.json            # Org-specific credentials — GITIGNORED, never commit
├── build.sh                 # Builds dist/miinto-secoda-analyst.mcpb
└── server/
    └── main.py              # Launcher script (required by DTX schema)
```

## Creating an org-specific bundle

1. Copy the template and fill in your credentials:

```bash
cp bundle/manifest.template.json bundle/manifest.json
```

Edit `bundle/manifest.json` and replace the `user_config` placeholders with your values:
- `API_TOKEN` — your Secoda API token
- `API_URL` — your Secoda API base URL
- `AI_PERSONA_ID` — your Secoda AI persona UUID (optional)

2. Build the bundle:

```bash
chmod +x bundle/build.sh
./bundle/build.sh
```

This creates `dist/miinto-secoda-analyst.mcpb`.

3. Install: drag and drop the `.mcpb` file onto **Claude Desktop → Settings → Developer**.

## Security

- `bundle/manifest.json` is gitignored — it contains credentials and must never be committed.
- `dist/` is gitignored — built bundles have credentials baked in.
- Only `manifest.template.json` (with placeholder variables) is committed.
