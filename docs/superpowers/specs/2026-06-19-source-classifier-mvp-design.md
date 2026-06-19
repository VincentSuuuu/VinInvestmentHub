# Source Classifier MVP Design

## Goal

Build the first conservative version of an external Source Classifier for `VincentWorkPlaceVer2.0`.

The MVP should reduce manual tagging work when adding sources to Notion. It should classify a source into suggested taxonomy fields, show the reasoning, and sync suggestions back to the Notion `Sources` database without automatically overwriting confirmed fields or modifying thesis relations.

## Product Context

`VincentWorkPlaceVer2.0` is evolving from a research archive into an investment research command center. The current research loop is:

```text
Source -> Evidence -> Interpretation -> Thesis -> Decision -> Review
```

The external classifier sits at the beginning of that loop. It handles source intake and triage so the Notion homepage can show what needs review before a source becomes a research note or thesis input.

## MVP Scope

The first version only supports:

- Paste a source URL or source text into a local web page.
- Run a classification pass.
- Display suggested classification fields with confidence and reasoning.
- Allow the user to edit the suggestions before sync.
- Sync the result to Notion `Sources`.
- Support a triage view in Notion through new suggested-classification fields.

The first version does not support:

- Automatic writes to final confirmed taxonomy fields.
- Automatic thesis relation edits.
- Automatic open-question relation edits.
- Automatic research note generation.
- Duplicate detection.
- Bulk classification.
- Browser extension capture.

## Notion Changes

Add lightweight fields to `Sources`:

- `Classification Status`: select with `Unclassified`, `Suggested`, `Confirmed`, `Needs Review`
- `Suggested Theme`: text
- `Suggested Geography`: text
- `Suggested Asset Class`: text
- `Suggested Entities`: text
- `Suggested Taxonomy L1`: text
- `Suggested Taxonomy L2`: text
- `Suggested Taxonomy L3`: text
- `Classification Confidence`: select with `High`, `Medium`, `Low`
- `Classification Reason`: text
- `Classifier Run At`: date

The existing final fields remain the source of truth:

- `Source Type`
- `Processing Status`
- `Reliability`
- `Bias`
- `Related Notes`
- `Related Events`

The classifier writes only the suggested fields and `Classification Status`.

## Homepage Blueprint

Add a `Source Triage` section near the top of the Notion homepage.

Recommended linked views:

- `Unclassified Sources`
  - Filter: `Classification Status` is empty or `Unclassified`
  - Sort: created time descending
- `Suggested, Waiting Confirmation`
  - Filter: `Classification Status` is `Suggested`
  - Show: name, source type, suggested theme, suggested entities, confidence
- `Low Confidence`
  - Filter: `Classification Confidence` is `Low`
  - Show: name, reason, suggested L1/L2/L3
- `Ready To Convert`
  - Filter: `Classification Status` is `Confirmed` and `Processing Status` is not `Linked`

## External App

The local app is a small Python web service with a static web interface.

Responsibilities:

- Load valid taxonomy options from local configuration.
- Accept user input for URL, title, and raw text.
- Classify the source using an LLM provider through a small provider interface.
- Validate model output against a strict JSON schema.
- Render suggestions in the browser.
- Let the user edit the suggestions.
- Sync suggestions to Notion through the Notion API.

## Classification Output

The model output must be normalized into this shape:

```json
{
  "source_type": "News",
  "theme": ["US-China Trade", "Policy"],
  "geography": ["US", "China"],
  "asset_class": ["Macro", "Equity"],
  "entities": ["Tariff", "US Treasury", "China exports"],
  "taxonomy_l1": ["Policy"],
  "taxonomy_l2": ["US-China Trade"],
  "taxonomy_l3": ["Tariff escalation"],
  "confidence": "Medium",
  "reason": "The source focuses on tariff policy and its market impact across US-China trade.",
  "needs_review": true
}
```

Rules:

- `taxonomy_l1` should be broad and conservative.
- `taxonomy_l2` can be more specific when evidence is clear.
- `taxonomy_l3` should be sparse and can be empty.
- `needs_review` is true when confidence is `Low` or when the model finds competing categories.
- The model should prefer under-classification over over-classification.

## Data Flow

```text
User input -> content extraction -> taxonomy-aware prompt -> JSON validation
-> editable review form -> Notion sync -> Source Triage view
```

## Safety And Data Hygiene

- Never write suggested fields into final fields automatically.
- Never create or modify thesis relations in MVP.
- Never delete or overwrite existing Notion content.
- Preserve raw model output in local logs only when the user enables debug mode.
- Keep Notion credentials in `.env`, never in source code.

## Success Criteria

- A user can classify one pasted source and sync it to Notion.
- Invalid model output is rejected with a useful error message.
- Low-confidence results are routed to `Needs Review`.
- The Notion `Sources` database can show a triage queue using the new fields.
- The implementation can run locally from `D:\Documents\NotionRebuild`.
