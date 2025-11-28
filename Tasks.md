# Tasks – MSCIS Starter Kit Automatisierung & KI

## Codex Task Tracker

| Nr. | Aufgabe | Status | Ergebnis |
| --- | ------- | ------ | -------- |
| 1 | Prompt-Verzeichnis inkl. ChatGPT-/Claude-Templates angelegt (`src/mscistk/generate/prompts/*`) | erledigt | Stile definieren die Tonalität für Newsletter & LinkedIn. |
| 2 | Lokalen LLM-Client + Adapter implementiert (`src/mscistk/ai/local_llm.py`) | erledigt | HTTP-Client (Ollama-kompatibel) inkl. Fehlerbehandlung und Konfig. |
| 3 | `generate/enhance.py` erstellt, Settings um AI-Block erweitert | erledigt | CLI wertet Settings aus, ruft lokales LLM oder kopiert bei `--skip-llm`. |
| 4 | Tasks.md & README Hinweise ergänzt, um KI-/Automation-Setup zu dokumentieren | erledigt | README verweist auf private Actions + lokale LLM-Schritte, Tasks-Datei führt Fortschritt. |

## 1. Gesamtziele
- GitHub Actions Workflow privat (kostenfrei im Rahmen des Freikontingents) betreiben, alternativ lokal ausführen.
- Lokales LLM für Textgestaltung (Newsletter, LinkedIn, Dossiers) nutzen und Ausgaben am Stil von ChatGPT/Claude ausrichten.
- Minimalen manuellen Aufwand: Feeds ziehen, Scoring, Templates rendern, KI-Veredelung, Obsidian-Ausgabe.

## 2. GitHub Actions Setup (kostenbewusst)
1. **Repository-Einstellungen prüfen**: sicherstellen, dass das Repo privat ist und GitHub Actions in `Settings > Actions > General` aktiviert ist.
2. **Contingent einplanen**: Privat-Repos auf GitHub Free erhalten 2.000 Runner-Minuten/Monat (Ubuntu); darüber hinaus pausiert der Workflow → ggf. `workflow_dispatch` und lokale Ausführung als Fallback nutzen.
3. **Workflow anpassen** (`workflows/ci.yml`):
   - Cron auf gewünschte Frequenz setzen (z. B. `0 6 * * *`).
   - Optional `if: github.repository_owner == '<dein-account>'` ergänzen, damit Forks nicht laufen.
   - Outputs als Artefakt (`actions/upload-artifact`) oder Push in Obsidian-Verzeichnis exportieren.
4. **Secrets hinterlegen** (`Settings > Secrets and variables > Actions`):
   - `MSRC_API_KEY`, `GITHUB_TOKEN` (standard), optionale LinkedIn/Trends Keys (Platzhalter erlaubt, wenn nicht genutzt).
5. **Kostenfreier Modus dokumentieren**: README ergänzen mit Hinweis auf Minutenlimit + Option, Workflow zu deaktivieren oder selbstgehostete Runner (lokal) zu verwenden.
6. **Lokaler Runner (optional)**:
   - `actions-runner` unter macOS/Linux installieren, Repo registrieren.
   - Runner als Dienst starten, damit Workflows ohne GitHub-Minuten laufen.

## 3. Lokales LLM für Textgestaltung
1. **LLM-Container wählen**: z. B. `ollama` mit einem freien Modell (Mixtral, Llama) oder LM Studio. Ziel: keine Cloud-Kosten.
2. **Prompt-Presets definieren** (`src/mscistk/generate/prompts/` erstellen):
   - Newsletter Prompt im Stil von ChatGPT.
   - LinkedIn Prompt im Stil von Claude (klar strukturierte Absätze, CTA, Hashtags).
3. **KI-Adapter schreiben** (`src/mscistk/ai/local_llm.py`):
   - Erwartet Prompt + Kontext (JSON).
   - Sendet Request an lokalen HTTP-Endpunkt (`http://127.0.0.1:11434/api/generate` für Ollama).
   - Fallback: überspringen, wenn Endpoint nicht läuft (CLI-Flag `--skip-llm`).
4. **Integration in Pipeline**:
   - Nach `generate/render.py` Schritt ein Skript `generate/enhance.py` einfügen: lädt Markdown, ruft lokales LLM zur Stil-Optimierung auf, schreibt Resultat nach `out/`.
   - Prompt-Parameter (Ton, Sprache, Länge) aus `settings.yaml` ziehen.
5. **Verweis auf ChatGPT/Claude**:
   - In README erklären, dass lokale Modelle verwendet werden, aber die Prompts auf den Stil und die Struktur von ChatGPT bzw. Claude referenzieren (kein API-Schlüssel nötig).

## 4. Nutzung mit Codex (Umsetzungsschritte)
1. **Umgebung vorbereiten**:
   - `python -m venv .venv && source .venv/bin/activate`
   - `pip install -r requirements.txt`
2. **Konfig anpassen**:
   - `src/mscistk/config/settings.example.yaml` nach `settings.local.yaml` kopieren.
   - Feeds, Scores, Ausgabepfade setzen.
3. **Automationslauf lokal testen**:
   - `python src/mscistk/ingest/rss_ingest.py src/mscistk/config/settings.local.yaml > out/rss.json`
   - `python src/mscistk/generate/render.py --settings src/mscistk/config/settings.local.yaml`
   - `python src/mscistk/generate/enhance.py --model local-chatgpt --style linkedin`
4. **GitHub Actions dry-run**:
   - `act` lokal oder Workflow per `workflow_dispatch`.
5. **Obsidian-Sync**:
   - `out/Obsidian` nach `/MicrosoftSecurity/...` kopieren oder Symlink setzen.
6. **Kontinuierliche Pflege**:
   - Tasks abhaken, wenn Codex die jeweiligen Schritte umgesetzt hat.
   - Neue Tasks bei Bedarf in dieser Datei ergänzen.

## 5. Entscheidungsfragen für den User
- Welche Frequenz/Grenzwerte soll der GitHub-Workflow haben?
- Welche lokalen Modelle (Größe, Sprache) sind zulässig?
- Darf das lokale LLM persistent Kontextdaten speichern?
- In welcher Sprache (DE/EN) sollen Standard-Outputs sein?

## Next Steps bis zum laufenden Setup
1. **Eigene Settings ableiten**: `cp src/mscistk/config/settings.example.yaml src/mscistk/config/settings.local.yaml` und Feeds, Tokens, sowie `ai`-Block anpassen (Endpoint, Modellname, Sprache).
2. **Virtuelle Umgebung**: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.
3. **Lokales LLM starten**: z. B. `ollama run llama3` oder gewünschtes Modell herunterladen und den Dienst (`ollama serve`) bzw. LM Studio REST-API aktiv halten.
4. **Render-Pipeline testen**:
   - `python src/mscistk/ingest/rss_ingest.py src/mscistk/config/settings.local.yaml > out/rss.json`
   - `python src/mscistk/generate/render.py --settings src/mscistk/config/settings.local.yaml`
   - `python src/mscistk/generate/enhance.py --settings src/mscistk/config/settings.local.yaml --input-dir out --output-dir out/ai --style newsletter`
5. **Obsidian-Sync prüfen**: `out/ai` Inhalte ins Vault kopieren oder Symlink setzen (`ln -s $(pwd)/out/ai /Pfad/zum/Obsidian/MicrosoftSecurity`).
6. **GitHub Actions aktivieren**:
   - Secrets setzen (`MSRC_API_KEY`, ggf. weitere).
   - Cron und `workflow_dispatch` kontrollieren; optional self-hosted Runner registrieren, falls keine Minuten verbraucht werden sollen.
7. **Review & Monitoring**:
   - Erste Outputs manuell gegen Quellen prüfen.
   - README/Tasks regelmäßig aktualisieren, wenn neue Modelle/Prompts oder Workflows hinzukommen.
