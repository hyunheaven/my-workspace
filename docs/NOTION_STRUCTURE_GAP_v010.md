# Comparison — Notion's Page-First model vs Enterprise AI Workspace

Reference page: https://app.notion.com/p/d662c59193db41c0b1213b79620e75a2
Reference was inspected for functional structure **only**. No original page content or third-party assets are redistributed in this project.

| Dimension | Reference Notion behavior | v0.9 | v0.10 |
| --- | --- | --- | --- |
| Main working surface | Editable page with blocks | Separate function panels | Page Canvas + Sidebar tree |
| Getting Started | Editable content | Static help page | Newly created original editable onboarding page |
| Hierarchy | Inline child pages plus sidebar navigation | Separate Page Tree screen | Sidebar nested page list + Page Tree management screen |
| Page composition | Heading, todo, toggle, etc. | Template fields | Nine text-only block types, manually saved |
| Inline Database Views | Tables, boards, calendars on pages | Separate app modules | Deferred |
| Rich text | Inline formatting, slash commands | Form inputs | Textareas; minimal '/' shortcut for heading only |
| Collaboration | Shared editing | Not implemented | Not implemented; requires approved central infra |
| Multimedia | Broad support in Notion | Disabled in the local app | Still explicitly disabled |

Do not equate current Page Canvas with a complete Notion replica. Next decision should be about a **domain schema**, not cosmetic pixel copying.
