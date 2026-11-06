---
name: linkedin-quote-card
description: Generate an Alta Beacon LinkedIn quote card in Canva by cloning Chad Dalton's "LinkedIn Quote Card" template, replacing the quote text, exporting a lossless PNG at 1200×1500, and saving it into the Chad-LinkedIn-Content workspace's `quote-cards/` folder with a filename that ties back to the Post_Library. Use whenever the user wants a quote card, pull-quote graphic, or shareable image for a LinkedIn post — phrases like "make a quote card", "build the card for this post", "quote graphic in Canva", "download the card". Requires Canva MCP tools (mcp__claude_ai_Canva__*).
---

# LinkedIn Quote Card — Canva template automation

Turns a one-line quote into a downloadable PNG using Chad's existing branded template. The template already has his avatar, name (`Chad Dalton`), and handle (`@dynamicschad`) locked in — only the quote text changes per post.

## Inputs
- **Quote text** — the single line that goes on the card. Ask the user if not provided. Keep it short enough to fit two lines at the template's font size (~65-75 characters is the sweet spot; the box will wrap up to ~3 lines but 4+ looks cramped).
- **Export format** (optional) — defaults to PNG, 1200×1500, lossless, opaque background. Only deviate if the user asks.

## Steps

1. **Find the template.**
   Call `mcp__claude_ai_Canva__search-designs` with `query: "LinkedIn Quote Card"`, `sort_by: relevance`.
   Take the top result whose title is exactly `LinkedIn Quote Card`.
   The known ID is `DAGx0xobY0Q` — if the search returns that ID, skip straight to step 2. If it doesn't come back (template renamed / deleted / new account), stop and tell the user.

2. **Copy the template** so edits don't touch the source.
   `mcp__claude_ai_Canva__copy-design` with the template's design ID. Grab the new design's ID and `edit_url` from the response.

3. **Open an editing transaction on the copy.**
   `mcp__claude_ai_Canva__start-editing-transaction` with the copied design ID.
   Save the `transaction_id` and the `pages` array from the response — both are required for the next call.

4. **Identify the quote text element.** The response lists three text elements. Pick the one whose `regions[0].text` is **neither** `Chad Dalton` **nor** starts with `@` — that's the quote body. Do not hardcode element IDs; they can drift.

5. **Show the current thumbnail** to the user (from the `thumbnails[0].url` field) so they can see the "before" state. This is a Canva requirement.

6. **Replace the quote text.**
   `mcp__claude_ai_Canva__perform-editing-operations` with:
   - `transaction_id` from step 3
   - `page_index: 1`
   - `pages` echoed back from step 3
   - one operation: `{ "type": "replace_text", "element_id": "<quote element id>", "text": "<user's quote>" }`

7. **Show the updated thumbnail** from the response so the user can eyeball the wrap and confirm. If it looks bad (text overflows or wraps awkwardly), offer to tighten the wording rather than resizing the box.

8. **Commit.**
   `mcp__claude_ai_Canva__commit-editing-transaction` with the transaction ID.

9. **Export.**
   `mcp__claude_ai_Canva__export-design` with the copied design ID and:
   ```json
   { "type": "png", "width": 1200, "height": 1500, "lossless": true }
   ```
   Do not set `transparent_background` unless the user asks — the template has a navy background and needs it opaque.

10. **Download to the workspace.** Save the PNG into `c:/Users/ChadDalton/source/repos/Chad-LinkedIn-Content/quote-cards/` (create the folder if it doesn't exist) using `curl -s -o <path> "<export url>"`. Filename convention:

    ```
    YYYY-MM-DD-<short-slug>.png
    ```

    - `YYYY-MM-DD` = the post's publish date if known, otherwise today.
    - `<short-slug>` = 3-5 kebab-case words pulled from the quote, distinctive enough to match the Post_Library entry (e.g. `security-last-tested-first-needed`, `azure-subscription-cleanup-orphans`).

    This mirrors how `Post_Library.md` indexes posts by `MM/DD/YY — Topic [Tier]` — same date-first ordering, so scanning the folder lines up with scanning the Library.

11. **Return** the local file path (as a clickable relative link so it opens in VS Code), the Canva `edit_url` from step 2, and the raw download URL as a backup. Note the raw URL is a short-lived signed S3 link (~12 hours); the local copy is the durable artifact.

## Notes
- Do **not** edit the original template design (`DAGx0xobY0Q`). Always work on a copy.
- The template is a fixed-page (non-responsive) design, so `replace_text`, `find_and_replace_text`, `format_text`, `update_fill`, `resize_element`, and `position_element` are all allowed if the user asks for a variant.
- Name/handle live in separate text elements. If the user ever asks to change author attribution, target those two elements the same way.
- If the post gets published on a different date than the draft date used in the filename, rename the file at publish time so it still lines up with the Post_Library section header.
