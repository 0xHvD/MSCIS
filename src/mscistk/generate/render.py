import os, yaml, json, datetime
from jinja2 import Environment, FileSystemLoader

def render_template(tpl_dir, tpl_name, data):
    env = Environment(loader=FileSystemLoader(tpl_dir), autoescape=False, trim_blocks=True, lstrip_blocks=True)
    tpl = env.get_template(tpl_name)
    return tpl.render(**data)

if __name__ == "__main__":
    import sys, pathlib
    tpl_dir = "src/mscistk/generate/templates"
    demo = {
        "date": datetime.date.today().isoformat(),
        "items": [{
            "title": "Soft Delete für Conditional Access Policies",
            "why": "Fehlkonfigurationen lassen sich schneller rückgängig machen",
            "what_changed": "Public Preview für Soft Delete/Restore",
            "impact": "Schnellere DR bei Policy-Fails",
            "actions": ["Pilot-Mandant anlegen", "Runbook für Restore erstellen"],
            "links": [{"name":"What's new Entra","url":"https://learn.microsoft.com/en-us/entra/fundamentals/whats-new"}]
        }]
    }
    md = render_template(tpl_dir, "newsletter.md.j2", demo)
    out = "examples/newsletter_demo.md"
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    open(out, "w", encoding="utf-8").write(md)
    print(out)
