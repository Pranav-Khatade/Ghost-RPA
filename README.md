<div align="center">

# GhostRPA Studio

### Local-first browser automation powered by vision-language models.

Describe a browser task in natural language. GhostRPA uses a local vision model to interpret the page, plan visual actions, and verify what happened.

<p>
  <a href="https://github.com/Pranav-Khatade/Ghost-RPA"><img src="https://img.shields.io/badge/Project-GhostRPA-111827?style=for-the-badge" alt="GhostRPA"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-16a34a?style=for-the-badge" alt="MIT License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="https://playwright.dev/python/"><img src="https://img.shields.io/badge/Browser-Playwright-2EAD33?style=for-the-badge" alt="Playwright"></a>
  <a href="https://ollama.com/"><img src="https://img.shields.io/badge/Inference-Ollama-black?style=for-the-badge" alt="Ollama"></a>
</p>

</div>

## Table of Contents

- [Overview](#overview)
- [Why GhostRPA?](#why-ghostrpa)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Clone the Repository](#1-clone-the-repository)
  - [Create a Virtual Environment](#2-create-a-virtual-environment)
  - [Install Dependencies](#3-install-dependencies)
  - [Set Up Ollama](#4-set-up-ollama)
  - [Launch the Dashboard](#5-launch-the-dashboard)
- [Using GhostRPA](#using-ghostrpa)
- [Configuration](#configuration)
- [Repository Structure](#repository-structure)
- [Troubleshooting](#troubleshooting)
- [Safety, Privacy, and Limitations](#safety-privacy-and-limitations)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Issues and Support](#issues-and-support)
- [License](#license)
- [Author](#author)

---

## Overview

**GhostRPA Studio** is an autonomous, local-first web automation and vision agent designed to execute browser workflows from natural-language instructions.

Instead of depending entirely on brittle CSS or XPath selectors, GhostRPA uses a screenshot-based workflow: a local Vision-Language Model (VLM) interprets the visible page and proposes actions, while Playwright performs browser interactions. The application then captures the updated page to check whether the action appears to have worked.

The repository includes a FastAPI dashboard for submitting a target URL and goal, viewing execution updates, and inspecting visual debug frames.

### At a glance

| Attribute | Details |
|---|---|
| Project | GhostRPA Studio |
| Category | Browser automation / RPA / vision agents |
| Language | Python |
| Web application | FastAPI + Uvicorn |
| Browser automation | Playwright (synchronous API) |
| Vision inference | Local Ollama model |
| Image handling | Pillow |
| Validation / models | Pydantic |
| Default local dashboard | `http://localhost:8000` |
| License | MIT |

## Why GhostRPA?

Traditional browser automation often relies on selectors tied to the page's DOM structure. Those selectors can break when a website changes its layout or markup. GhostRPA explores a visual alternative: use the page as a person sees it, ask a VLM to identify the next interaction, and verify the resulting state.

The local-first design also aims to keep page screenshots and model inference on the user's machine when a local Ollama model is used. Actual privacy depends on the configured model, application behavior, and any external sites or services the user interacts with.

## Features

| Feature | Description | Why it matters |
|---|---|---|
| Visual element grounding | Uses screenshots and pixel coordinates to plan interactions | Reduces dependence on fragile CSS/XPath selectors |
| Local VLM inference | Connects to a vision-capable model served by Ollama | Supports local inference without sending screenshots to a hosted model API by default |
| Natural-language goals | Accepts a target URL and a plain-language task through the dashboard | Makes automation goals easier to express |
| Playwright execution | Runs browser actions such as clicking, typing, scrolling, and waiting | Connects visual planning to real browser interaction |
| State verification | Captures the page after actions to check for visible changes | Helps detect actions that may not have succeeded |
| Recovery attempts | Can attempt corrective actions when visual progress is not detected | Makes workflows more resilient to transient UI states |
| FastAPI dashboard | Provides a browser-based interface for launching and monitoring runs | Makes the agent easier to operate and debug |
| Visual debug frames | Displays annotated frames and coordinate overlays | Helps inspect why an action was selected |
| Cross-platform intent | Uses Python and Playwright components available across major desktop platforms | Supports development on Windows, Linux, and macOS, subject to dependency setup |

> **Important:** Visual automation is probabilistic. A model can misidentify controls, select the wrong coordinates, or misunderstand the page. Review automation runs and use safe test environments before relying on the agent for important workflows.

## Technology stack

| Technology | Role |
|---|---|
| Python 3.10+ | Core application and automation logic |
| FastAPI | HTTP server and dashboard backend |
| Uvicorn | ASGI application server |
| Playwright | Chromium launch and browser interactions |
| Ollama | Local model serving |
| Vision-Language Model | Interprets screenshots and proposes visual actions |
| Pydantic | Data validation and structured models |
| Pillow | Image processing and debug-frame handling |
| Requests / HTTPX | HTTP communication, where used by the application |

## Architecture

At a high level, GhostRPA follows this flow:

```text
┌───────────────────────────┐
│ User goal + target URL    │
│ FastAPI dashboard         │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ Browser session           │
│ Playwright + Chromium     │
└─────────────┬─────────────┘
              │ Screenshot
              ▼
┌───────────────────────────┐
│ Visual planning           │
│ Local VLM through Ollama  │
└─────────────┬─────────────┘
              │ Action + coordinates
              ▼
┌───────────────────────────┐
│ Action execution          │
│ Click / type / scroll / wait
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ State verification        │
│ New screenshot + recovery │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ Dashboard execution stream│
│ Debug frames / status     │
└───────────────────────────┘
```

This is a conceptual overview of the intended execution flow, not a guarantee that every task succeeds or that every action is recoverable.

### Core components

| Component | Responsibility |
|---|---|
| `app.py` | FastAPI application and web dashboard |
| `vision.py` | Visual planning and state-verification functionality |
| `main.py` | Main automation logic / execution entry point |
| `run.py` | Additional runner or launch logic |
| `engine/` | Supporting engine modules, including visual debug utilities |
| `requirements.txt` | Python dependency declarations |

The codebase may evolve. Check the repository for the latest source files and their current responsibilities.

## Quick Start

### Prerequisites

Install the following before running GhostRPA:

| Requirement | Purpose | Notes |
|---|---|---|
| Python 3.10+ | Runs the application | Use a supported Python installation |
| Git | Clones the repository | Optional if downloading the source as an archive |
| Ollama | Serves the local vision model | Install from [ollama.com](https://ollama.com/) |
| Vision-capable model | Interprets browser screenshots | Select a model supported by your Ollama setup |
| Playwright Chromium | Provides the browser runtime | Install using the Playwright command below |

### 1. Clone the repository

```bash
git clone https://github.com/Pranav-Khatade/Ghost-RPA.git
cd Ghost-RPA
```

### 2. Create a virtual environment

**Windows — PowerShell**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

**Linux / macOS**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

Install the dependencies listed in the repository:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install the Playwright Chromium browser:

```bash
python -m playwright install chromium
```

If the browser installation fails, consult the [Playwright Python documentation](https://playwright.dev/python/docs/intro).

### 4. Set up Ollama

Install and start Ollama, then download a vision-capable model supported by your local setup.

For example, the current README uses `moondream` as an example:

```bash
ollama pull moondream
ollama run moondream
```

Keep Ollama running while you use GhostRPA. If your configuration or source code expects a different model name, use that model instead. Model availability, hardware requirements, and response quality vary.

### 5. Launch the dashboard

From the repository root, with the virtual environment activated:

```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Open:

**http://127.0.0.1:8000**

The command above binds the dashboard to the local machine. If you intentionally need access from another device on a trusted network, review the security implications before changing the host to `0.0.0.0`.

## Using GhostRPA

1. Start Ollama and confirm the selected vision model is available.
2. Start the FastAPI application.
3. Open the local dashboard.
4. Enter the target URL.
5. Describe the task as a clear, bounded natural-language goal.
6. Launch the agent run.
7. Monitor the execution stream and inspect visual debug frames.
8. Verify the result in the browser before treating the workflow as complete.

### Example task

For a safe public page, a task could be:

```text
Target URL: https://news.ycombinator.com

Goal: Locate the search field, enter "AI agents", and show the resulting page.
```

This is an illustrative example, not a claim of a verified successful run. The exact outcome depends on the website, the model, and the current implementation.

### Tips for better instructions

| Less precise | Better instruction |
|---|---|
| “Use this website.” | “Open the target page and locate the search field.” |
| “Fill the form.” | “Enter the provided test values into the named fields and stop before submission.” |
| “Find something.” | “Search for the specified term and report the visible result titles.” |

Keep instructions specific. For consequential actions—such as purchases, sending messages, deleting data, changing account settings, or submitting forms—require human review and confirmation.

## Configuration

GhostRPA depends on the local model and the settings implemented in the repository.

| Setting | What to check |
|---|---|
| Ollama availability | Confirm the local Ollama service is running |
| Model name | Ensure the configured model matches a model installed in Ollama |
| Browser runtime | Confirm Playwright Chromium is installed |
| Dashboard port | Default example: `8000` |
| Target website | Use a permitted site and an account/test environment you are authorized to access |
| Runtime screenshots | Review where debug images are stored and how long they are retained |

Use the repository's source code as the authority for exact configuration names. No environment-variable names are documented here unless confirmed in the current source.

## Repository structure

The repository includes the following top-level files and components:

```text
Ghost-RPA/
├── engine/
│   └── ...                 # Supporting automation/debug components
├── app.py                  # FastAPI dashboard and server application
├── main.py                 # Main automation logic
├── run.py                  # Runner / launch-related logic
├── vision.py               # Vision planning and verification
├── requirements.txt        # Python dependencies
├── LICENSE                 # MIT license
└── README.md               # Project documentation
```

This is a simplified view. Hidden files and additional runtime directories may exist locally or be excluded from version control.

## Troubleshooting

| Problem | What to check |
|---|---|
| `ModuleNotFoundError` | Activate the correct virtual environment and run `python -m pip install -r requirements.txt` |
| `uvicorn` command not found | Run `python -m uvicorn app:app --port 8000` from the repository root |
| Dashboard does not open | Check the terminal for startup errors and confirm port `8000` is not already in use |
| Chromium fails to launch | Run `python -m playwright install chromium` |
| Ollama connection fails | Confirm Ollama is running and accessible from the same machine |
| Model not found | Pull a supported model and make sure the configured model name matches |
| Model returns invalid actions | Check model compatibility, prompt/output expectations, and the execution logs |
| Agent clicks the wrong place | Inspect the screenshot and debug overlay; simplify the task and use a less ambiguous page |
| No visible progress | Check whether the page loaded, whether an overlay or modal blocks it, and whether the model correctly understood the screenshot |

If a problem persists, open a GitHub issue with the operating system, Python version, reproducible steps, and relevant sanitized logs. Never include credentials, session cookies, API keys, or private page screenshots.

## Safety, privacy, and limitations

GhostRPA is designed around local vision inference, but **local-first does not mean risk-free**.

- **Browser actions have real effects.** A click or form submission can change data, send a message, or trigger a transaction.
- **Use least privilege.** Prefer test accounts and browser profiles without access to sensitive services.
- **Review before consequential actions.** Require human approval for payments, purchases, account changes, deletion, or submission of important information.
- **Treat page content as untrusted.** A website may display misleading instructions. Do not let page text override the user's intended task or safety boundaries.
- **Protect local artifacts.** Screenshots and debug frames can contain personal information. Review storage paths, retention, and access permissions.
- **Verify model behavior.** VLMs may hallucinate controls, misread text, or return inaccurate coordinates.
- **Check the target site's rules.** Automate only websites and accounts you are authorized to use, and respect applicable terms and access restrictions.
- **No guarantee of success.** UI changes, network latency, pop-ups, and model variation can interrupt a workflow.

GhostRPA is an experimental developer project and should not be treated as a fully secure, production-hardened automation platform without further validation.

## Roadmap

Potential improvements to consider:

- [ ] Add automated tests for visual planning and action execution.
- [ ] Document supported VLMs and expected response formats.
- [ ] Add explicit human-confirmation gates for high-impact actions.
- [ ] Add configurable action timeouts, retries, and maximum-step limits.
- [ ] Improve structured logs and failure diagnostics.
- [ ] Add example screenshots or a short demo recording using non-sensitive pages.
- [ ] Document screenshot storage, retention, and cleanup behavior.
- [ ] Add reproducible end-to-end examples and a troubleshooting guide.

These are suggested future improvements, not claims that the features are already implemented.

## Contributing

Contributions and practical feedback are welcome.

1. Fork the repository.
2. Create a focused branch.
   ```bash
   git checkout -b feature/your-change
   ```
3. Keep changes small and explain the problem they solve.
4. Run the application and verify the affected workflow where practical.
5. Open a pull request with a concise summary, testing notes, and screenshots only when they contain no sensitive information.

For bug reports, include your environment, steps to reproduce, expected behavior, actual behavior, and sanitized logs.

## Issues and support

| Resource | Link |
|---|---|
| Source code | [Pranav-Khatade/Ghost-RPA](https://github.com/Pranav-Khatade/Ghost-RPA) |
| Issues and feature requests | [GitHub Issues](https://github.com/Pranav-Khatade/Ghost-RPA/issues) |
| Browser automation docs | [Playwright for Python](https://playwright.dev/python/) |
| Local model runtime | [Ollama](https://ollama.com/) |
| API framework | [FastAPI](https://fastapi.tiangolo.com/) |

## License

GhostRPA is distributed under the MIT License. See [`LICENSE`](./LICENSE) for the full license text.

## Author

**Pranav Khatade**

- GitHub: [@Pranav-Khatade](https://github.com/Pranav-Khatade)
- Project: [Ghost-RPA](https://github.com/Pranav-Khatade/Ghost-RPA)

---

<div align="center">

**Making browser automation more visual, adaptable, and locally controlled.**

If GhostRPA is useful to you, consider starring the repository.

</div>
