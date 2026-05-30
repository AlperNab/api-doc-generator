#!/usr/bin/env python3
"""
api-doc-generator — any codebase or route definitions → OpenAPI spec + human-readable docs
Supports: Express, FastAPI, Flask, Django, Rails — infers from code patterns
"""
import anthropic, json, re, sys
from pathlib import Path

SYSTEM = """You are a senior API architect and technical writer.
Generate complete API documentation from code or route definitions.

Rules:
- Infer request/response schemas from code patterns
- Generate realistic example values (not "string" as example)
- Include authentication details if detectable
- Add common error responses (400, 401, 403, 404, 500)
- Write descriptions a developer can actually use

Return ONLY valid JSON — no markdown, no explanation.

{
  "api_name": "string",
  "api_version": "string",
  "base_url": "string or null",
  "detected_framework": "express|fastapi|flask|django|rails|spring|other",
  "authentication": {
    "type": "bearer|api_key|oauth2|basic|none|unknown",
    "header": "Authorization|X-API-Key|string or null",
    "description": "how to authenticate"
  },
  "endpoints": [
    {
      "method": "GET|POST|PUT|PATCH|DELETE",
      "path": "/resource/{id}",
      "summary": "short action description",
      "description": "longer description of what this endpoint does",
      "tags": ["resource category"],
      "authentication_required": true_or_false,
      "path_params": [
        {"name":"id","type":"string|integer","required":true,"description":"string","example":"123"}
      ],
      "query_params": [
        {"name":"limit","type":"integer","required":false,"description":"string","default":"20","example":"50"}
      ],
      "request_body": {
        "required": true_or_false,
        "content_type": "application/json",
        "schema": {},
        "example": {}
      },
      "responses": {
        "200": {"description":"string","example":{}},
        "400": {"description":"Bad request — validation error","example":{"error":"string","details":[]}},
        "401": {"description":"Unauthorized","example":{"error":"Invalid or missing token"}},
        "404": {"description":"Not found","example":{"error":"Resource not found"}},
        "500": {"description":"Internal server error","example":{"error":"string"}}
      },
      "rate_limit": "string or null",
      "deprecated": false
    }
  ],
  "openapi_spec": {
    "openapi": "3.0.3",
    "info": {"title":"string","version":"string","description":"string"},
    "servers": [{"url":"string"}],
    "paths": {}
  },
  "data_models": [
    {
      "name": "ModelName",
      "description": "what this model represents",
      "properties": [
        {"name":"string","type":"string","required":true,"description":"string","example":"value"}
      ]
    }
  ],
  "quick_start": "code snippet showing the most common API call",
  "changelog_notes": ["inferred or stated version changes"],
  "confidence": 0.0
}"""

def generate(code_source: str, api_name: str = "", base_url: str = "") -> dict:
    client = anthropic.Anthropic()
    path = Path(code_source)
    if path.exists():
        if path.is_dir():
            # Collect route files
            route_files = []
            for ext in ["*.py","*.js","*.ts","*.rb"]:
                route_files.extend(path.rglob(ext))
            code = ""
            for f in sorted(route_files)[:20]:
                try:
                    content = f.read_text(encoding="utf-8",errors="replace")
                    if any(kw in content for kw in ["@app.route","router.","app.get","app.post","@router","path("]):
                        code += f"\n# === {f.name} ===\n{content[:3000]}\n"
                except Exception:
                    pass
            code = code[:40000]
        else:
            code = path.read_text(encoding="utf-8",errors="replace")[:40000]
        api_name = api_name or path.stem.replace("-"," ").replace("_"," ").title()
    else:
        code = code_source[:40000]

    context = f"API Name: {api_name}\n" if api_name else ""
    if base_url: context += f"Base URL: {base_url}\n"
    context += f"\nCode:\n{code}"

    resp = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=4096, system=SYSTEM,
        messages=[{"role":"user","content":f"Generate API documentation:\n\n{context}"}]
    )
    raw = re.sub(r'^```(?:json)?\s*','',resp.content[0].text.strip(),flags=re.MULTILINE)
    raw = re.sub(r'\s*```$','',raw,flags=re.MULTILINE)
    return json.loads(raw)

def to_openapi_yaml(r: dict) -> str:
    """Export the OpenAPI spec as YAML."""
    try:
        import yaml
        return yaml.dump(r.get("openapi_spec",{}), default_flow_style=False, allow_unicode=True)
    except ImportError:
        return json.dumps(r.get("openapi_spec",{}), indent=2)

def print_docs(r: dict):
    endpoints = r.get("endpoints",[])
    auth = r.get("authentication",{})
    print(f"\n{'═'*60}")
    print(f"  API DOCS — {r.get('api_name','?')} v{r.get('api_version','?')}")
    print(f"  Framework: {r.get('detected_framework','?')} | Endpoints: {len(endpoints)}")
    if r.get("base_url"): print(f"  Base URL: {r['base_url']}")
    print(f"  Auth: {auth.get('type','?')} — {auth.get('header','?')}")
    print(f"{'═'*60}")

    METHOD_COLOR = {"GET":"\033[92m","POST":"\033[94m","PUT":"\033[93m","PATCH":"\033[93m","DELETE":"\033[91m"}
    R = "\033[0m"
    for ep in endpoints:
        method = ep.get("method","?")
        color = METHOD_COLOR.get(method,"")
        auth_tag = " 🔒" if ep.get("authentication_required") else ""
        depr = " [DEPRECATED]" if ep.get("deprecated") else ""
        print(f"\n  {color}{method:<7}{R} {ep.get('path','?')}{auth_tag}{depr}")
        print(f"  {ep.get('summary','')}")
        if ep.get("description") and ep["description"] != ep.get("summary",""): print(f"  {ep['description'][:100]}")

        path_params = ep.get("path_params",[])
        if path_params: print(f"  Path: {', '.join(f\"{p.get('name','?')} ({p.get('type','?')})\" for p in path_params)}")
        query_params = ep.get("query_params",[])
        if query_params: print(f"  Query: {', '.join(f\"{p.get('name','?')}\" for p in query_params[:4])}")
        req_body = ep.get("request_body",{})
        if req_body.get("required"): print(f"  Body: {json.dumps(req_body.get('example',{}))[:80]}")
        responses = ep.get("responses",{})
        ok_resp = responses.get("200",{})
        if ok_resp.get("example"): print(f"  → {json.dumps(ok_resp.get('example',{}))[:80]}")

    models = r.get("data_models",[])
    if models:
        print(f"\n  DATA MODELS ({len(models)})")
        for m in models: print(f"  {m.get('name','')} — {m.get('description','')[:60]}")

    if r.get("quick_start"): print(f"\n  Quick start:\n  {r['quick_start'][:200]}")
    print(f"\n  Confidence: {int(r.get('confidence',0)*100)}%")
    print(f"{'═'*60}\n")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Generate API documentation from source code")
    p.add_argument("source", help="Source file, directory, or raw code")
    p.add_argument("--name","-n",default="")
    p.add_argument("--base-url","-u",default="")
    p.add_argument("--json",action="store_true")
    p.add_argument("--openapi","-o",help="Save OpenAPI spec to file")
    a = p.parse_args()
    r = generate(a.source, a.name, a.base_url)
    if a.openapi:
        Path(a.openapi).write_text(to_openapi_yaml(r),encoding="utf-8")
        print(f"OpenAPI spec saved to {a.openapi}")
    if a.json: print(json.dumps(r,indent=2,ensure_ascii=False))
    else: print_docs(r)
