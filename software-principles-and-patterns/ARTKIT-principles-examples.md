# ARTKIT: Good examples of SOLID, KISS, and DRY

Curated highlights from BCG-X-Official/artkit that demonstrate clean design in practice. These are positive examples you can show when teaching software principles. Links point to the upstream repo for quick inspection.

> Note: Links reference the `1.0.x` branch as of Nov 2025.

## 1) SRP — ChatHistory keeps one job small and clear

- What: `ChatHistory` is responsible only for storing and retrieving chat messages and enforcing a max length.
- Why it’s good: Tiny API, focused behavior, easy to test; no networking, caching, or model logic mixed in.
- Where:
  - Chat history class: https://github.com/BCG-X-Official/artkit/blob/1.0.x/src/artkit/model/llm/history/_history.py#L45-L125

## 2) OCP — Provider connectors extend a stable abstraction

- What: New model providers (OpenAI, Anthropic, Azure, Gemini, Hugging Face, vLLM, Ollama) subclass `ChatModelConnector` without changing the base.
- Why it’s good: The system is open to extension (new providers) but closed to modification (shared abstractions stay untouched).
- Where:
  - Base chat connector: https://github.com/BCG-X-Official/artkit/blob/1.0.x/src/artkit/model/llm/base/_llm.py#L176-L188
  - Example providers:
  - OpenAI: https://github.com/BCG-X-Official/artkit/blob/1.0.x/src/artkit/model/llm/openai/_openai.py
  - Anthropic: https://github.com/BCG-X-Official/artkit/blob/1.0.x/src/artkit/model/llm/anthropic/_anthropic.py
  - Azure OpenAI: https://github.com/BCG-X-Official/artkit/blob/1.0.x/src/artkit/model/llm/azure/_azureopenai.py
  - Hugging Face: https://github.com/BCG-X-Official/artkit/blob/1.0.x/src/artkit/model/llm/huggingface/_huggingface.py
  - vLLM: https://github.com/BCG-X-Official/artkit/blob/1.0.x/src/artkit/model/llm/vllm/_vllm.py
  - `Ollama`: https://github.com/BCG-X-Official/artkit/blob/1.0.x/src/artkit/model/llm/ollama/_ollama.py

## 3) DIP — Adapters and wrappers depend on abstractions

- What: The project programs against `ChatModel`/`CompletionModel` interfaces and composes capabilities via adapters/wrappers like `ChatFromCompletionModel`, `CachedChatModel`, and `HistorizedChatModel`.
- Why it’s good: High-level code stays decoupled from vendor SDKs; connectors hide client specifics behind stable contracts.
- Where:
  - Interfaces: https://github.com/BCG-X-Official/artkit/blob/1.0.x/src/artkit/model/llm/base/_llm.py
  - Chat-from-completion adapter: https://github.com/BCG-X-Official/artkit/blob/1.0.x/src/artkit/model/llm/_gen2chat.py#L70-L185
  - Cached chat wrapper: https://github.com/BCG-X-Official/artkit/blob/1.0.x/src/artkit/model/llm/_cached.py#L97-L157
  - Historized chat wrapper: https://github.com/BCG-X-Official/artkit/blob/1.0.x/src/artkit/model/llm/_historized.py

## 4) ISP — Separate small interfaces for different model types

- What: Distinct abstractions for LLM chat (`ChatModel`), LLM completion (`CompletionModel`), Vision (`VisionModel`), and Diffusion.
- Why it’s good: Callers only depend on the capabilities they use; no “god” interface.
- Where:
  - LLM base (chat/completion): https://github.com/BCG-X-Official/artkit/blob/1.0.x/src/artkit/model/llm/base/_llm.py
  - Vision base: https://github.com/BCG-X-Official/artkit/tree/1.0.x/src/artkit/model/vision/base
  - Diffusion base: https://github.com/BCG-X-Official/artkit/tree/1.0.x/src/artkit/model/diffusion/base

## 5) DRY — One caching engine used across modalities

- What: `CachedGenAIModel` centralizes cache mechanics; specialized wrappers reuse it for chat, vision, and diffusion.
- Why it’s good: Eliminates duplicated cache code, ensures consistent behavior, and simplifies maintenance.
- Where:
  - Cache engine: https://github.com/BCG-X-Official/artkit/blob/1.0.x/src/artkit/model/base/_adapter.py#L100-L182
  - Chat caching: https://github.com/BCG-X-Official/artkit/blob/1.0.x/src/artkit/model/llm/_cached.py#L97-L157
  - Vision caching: https://github.com/BCG-X-Official/artkit/blob/1.0.x/src/artkit/model/vision/_cached.py#L59-L102
  - Diffusion caching: https://github.com/BCG-X-Official/artkit/blob/1.0.x/src/artkit/model/diffusion/_cached.py#L65-L100

## 6) KISS — Simple, readable extraction of responses

- What: Helpers iterate completion choices and yield strings with minimal logic.
- Why it’s good: Straightforward behavior, easy to reason about and reuse.
- Where:
  - OpenAI responses: https://github.com/BCG-X-Official/artkit/blob/1.0.x/src/artkit/model/llm/openai/_openai.py#L182-L199
  - `Ollama` responses: https://github.com/BCG-X-Official/artkit/blob/1.0.x/src/artkit/model/llm/ollama/_ollama.py#L143-L160

---

## Opportunities to improve

- Unify OpenAI-style message formatting across providers
  - What: Centralize conversion of internal messages to provider-specific payloads (role/name/content; tools; function-calls).
  - Why: Reduces duplication and drift; simplifies adding new providers; improves test coverage via one shared formatter.

- Centralize error handling and retry policy
  - What: Extract common exceptions, retry/backoff, and rate-limit handling into a small shared utility used by all connectors.
  - Why: Ensures consistent behavior and logging; prevents subtle differences across providers; easier SLO tuning.

- Normalize streaming interfaces and chunk shapes
  - What: Provide a single iterator protocol and chunk data class for token/part streams across providers.
  - Why: Callers can handle streams uniformly; simplifies adapters and demos; improves composability.

- Factor shared request/response models
  - What: Define lightweight, provider-agnostic request/response DTOs (messages, tool calls, safety blocks) mapped at connector edges.
  - Why: Clarifies contracts; keeps core layers vendor-neutral; eases cross-provider testing.

- Consolidate provider configuration parsing
  - What: Standardize model name, endpoint, API version, and feature flags parsing (env → config → connector) in one place.
  - Why: Avoids repeated env/kwargs handling; reduces bugs and surprises; improves docs discoverability.

- Add cross-connector conformance tests
  - What: A minimal test matrix that runs the same prompts and asserts normalized outputs/metadata across connectors.
  - Why: Guards against regressions; proves LSP-style interchangeability; documents expected behavior.