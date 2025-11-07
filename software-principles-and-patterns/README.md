# Software Design Principles and Patterns - Demos (60 minutes)

This folder contains runnable, bite-sized Python demos to support a 60-minute session.
Each demo has a tiny main you can run directly. Use them to illustrate points live.

## Agenda & mapping

- 0-5 min - Overview and framing
  - Files: `00-overview/messy_code_bad.py`, `00-overview/messy_code_refactor.py`
- 5-15 min - Core design principles
  - SRP & OCP: `01-principles/srp_ocp_order_processor_bad.py`, `01-principles/srp_ocp_order_processor_good.py`
  - LSP & ISP: `01-principles/lsp_isp_bad.py`, `01-principles/lsp_isp_good.py`
  - DIP: `01-principles/dip_logger_demo.py`
  - DRY/KISS/YAGNI: `01-principles/dry_kiss_yagni_bad.py`, `01-principles/dry_kiss_yagni_good.py`
- 15-25 min - Interactive discussion
  - Use `smell_spotting.py` and the bad versions above for quick polls.
- 25-35 min - Transition to design patterns
  - Quick UML references in `../diagrams/ref.md`.
- 35-50 min - Deep-dive examples
  - Creational (Factory Method/Singleton): `02-patterns/factory_method_singleton.py`
  - Structural (Adapter/Facade): `02-patterns/adapter_facade.py`
  - Behavioral (Observer/Strategy): `02-patterns/observer_strategy.py`
- 50-55 min - Pattern selection exercise
  - Prompts are at the end of this README.
- 55-60 min - Wrap-up and takeaways

## How to run

Run any demo directly (Python 3.9+ recommended):

```bash
python software-principles-and-patterns/00-overview/messy_code_bad.py
python software-principles-and-patterns/00-overview/messy_code_refactor.py
python software-principles-and-patterns/01-principles/srp_ocp_order_processor_bad.py
python software-principles-and-patterns/01-principles/srp_ocp_order_processor_good.py
python software-principles-and-patterns/01-principles/lsp_isp_bad.py
python software-principles-and-patterns/01-principles/lsp_isp_good.py
python software-principles-and-patterns/01-principles/dip_logger_demo.py
python software-principles-and-patterns/01-principles/dry_kiss_yagni_bad.py
python software-principles-and-patterns/01-principles/dry_kiss_yagni_good.py
python software-principles-and-patterns/02-patterns/factory_method_singleton.py
python software-principles-and-patterns/02-patterns/adapter_facade.py
python software-principles-and-patterns/02-patterns/observer_strategy.py
```

Or run everything in sequence (optionally filter by substring):

```bash
python software-principles-and-patterns/run_all.py
# or only patterns
python software-principles-and-patterns/run_all.py patterns
```

Tip: Run a "bad" first, then the corresponding "good". Ask the audience what changed and why.

---

## 0-5 min - Overview & framing

- Show messy, tightly coupled code (bad) then the tiny, composable version (refactor).
- Emphasize: principles guide choices; patterns are reusable solutions, not rules.

Files:

- `00-overview/messy_code_bad.py`
- `00-overview/messy_code_refactor.py`

---

## 5-15 min - Core design principles

- SRP (Single Responsibility): One reason to change. Split concerns.
- OCP (Open/Closed): Open for extension, closed for modification.
- LSP (Liskov Substitution): Subtypes must honor contracts of supertypes.
- ISP (Interface Segregation): Prefer small, client-specific interfaces.
- DIP (Dependency Inversion): Depend on abstractions, not concretions.
- DRY/KISS/YAGNI: Avoid duplication, keep it simple, don’t build what you don’t need.

Files:

- `01-principles/srp_ocp_order_processor_bad.py`
- `01-principles/srp_ocp_order_processor_good.py`
- `01-principles/lsp_isp_bad.py`
- `01-principles/lsp_isp_good.py`
- `01-principles/dip_logger_demo.py`
- `01-principles/dry_kiss_yagni_bad.py`
- `01-principles/dry_kiss_yagni_good.py`

Activity idea: give the audience 60s to spot violations before running the "good" version.

---

## 25-35 min - Transition to patterns

- Principles = "why/when"; Patterns = "how/what."
- Three families: Creational, Structural, Behavioral.
- Use micro-demos to show intent, not production frameworks.

Files:

- `02-patterns/factory_method_singleton.py`
- `02-patterns/adapter_facade.py`
- `02-patterns/observer_strategy.py`

---

## 35-50 min - Deep-dive examples

- Factory Method/Singleton: Encapsulate creation and share a single instance when appropriate.
- Adapter/Facade: Isolate 3rd-party lib surface and provide a simplified entrypoint.
- Observer/Strategy: Decouple publishers/subscribers; make algorithms interchangeable.

Run each, then tweak inputs live to show extensibility.

---

## 50-55 min - Pattern selection exercise

- Need to notify multiple modules when state changes → Observer
- Need to pick coupon logic at runtime → Strategy
- Need to hide complex subsystem init → Facade
- Need to integrate legacy API with a clean interface → Adapter
- Need to manage creation based on type or configuration → Factory Method

Ask teams to justify their choice and tradeoffs.

---

## 55-60 min - Wrap-up

- Principles keep code clean; patterns offer reusable blueprints.
- Use patterns judiciously-prefer simple code until complexity demands a pattern.
- Homework: refactor a class using one SOLID principle + implement one pattern.

---

## Bonus: Bad-smell spotting snippet

Use `smell_spotting.py` for a quick "find-the-violations" warmup.
