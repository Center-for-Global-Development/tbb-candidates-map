# Analytics — TBB candidates map

Sent by `shared/cgd-embed.js`, the published CGD embed layer, unchanged. The
figure's identity comes from the root element:

```html
<html data-cgd-interactive-name="dtv-tbb-candidates-map">
```

Events go to the parent page (`https://www.cgdev.org`) and on to GTM/GA4. The
child sends nothing anywhere else, sets no cookies, and collects nothing about
the reader.

## Events

| Event | When | Fields |
|---|---|---|
| `interactive_view` | once, on load | `interactive_name` |
| `interactive_engagement` | on each committed action below | `interactive_name`, `action_type`, `action_label`, `action_value` |

## Engagement actions

| `action_type` | `action_label` | `action_value` | Fired when |
|---|---|---|---|
| `filter` | `skill_level` | `ALL`, `RQF 6+`, `RQF 3-5`, `RQF 1-2` | a skill-level button is pressed |
| `filter` | `shortage_list_only` | `true`, `false` | the shortage-list checkbox changes |
| `filter` | `occupation` | occupation name, or `ALL` | the occupation select changes |
| `select` | `country` | country name | a country is clicked, or chosen in "Find a country" |
| `download` | `country_counts` | occupation name, or `ALL` | the CSV is downloaded |

## Deliberately not instrumented

Hover, pointer movement, focus, tooltip opening, resize, fullscreen and
deselection. These are not committed actions; sending them would bury the
signal and inflate event volume. `action_value` is bounded: at most 144
occupation names and 26 country names, both drawn from the payload, so
cardinality cannot grow with traffic.
