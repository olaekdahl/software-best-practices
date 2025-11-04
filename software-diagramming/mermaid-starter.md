``` mermaid
%% MIT License
%% SPDX-License-Identifier: MIT
%% Author: Ola Ekdahl
%% Owner: Ascendient Learning
%% Year: 2025
%% Purpose: Reusable Mermaid template with stereotypes, palette, legend, and helpers.

%% Diagram
flowchart LR
  %% ---------- Palette ----------
  %% external : #FFFBE6 / #FFB000
  %% queue    : #E8F5E9 / #2E7D32
  %% db       : #E3F2FD / #1565C0
  %% boundary : #F3E5F5 / #6A1B9A

  %% ---------- ClassDefs (stereotype styles) ----------
  classDef external fill:#FFFBE6,stroke:#FFB000,stroke-width:2px;
  classDef queue    fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px,stroke-dasharray:3 2;
  classDef db       fill:#E3F2FD,stroke:#1565C0,stroke-width:2px;
  classDef boundary fill:#F3E5F5,stroke:#6A1B9A,stroke-width:2px,stroke-dasharray:5 3;

  %% ---------- “Helpers” (conventions) ----------
  %% Use :::stereotype after a node to assign its class.
  %% external:  A[Third-party API]:::external
  %% queue:     Q((Orders Queue)):::queue
  %% db:        D[(Orders DB)]:::db
  %% boundary:  B{{API Boundary}}:::boundary

  %% ---------- Example usage (delete below for new diagrams) ----------
  A[Payments Provider]:::external --> B{{API Gateway}}:::boundary
  B --> Q((Orders Queue)):::queue
  B --> D[(Orders DB)]:::db

  %% ---------- Legend ----------
  subgraph Legend
    direction TB
    L1[External]:::external
    L2((Queue)):::queue
    L3[(Database)]:::db
    L4{{Boundary}}:::boundary
  end
```
