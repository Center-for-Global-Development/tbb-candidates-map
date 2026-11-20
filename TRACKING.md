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
| `filter` | `occupation_band` | `ALL`, `RQF 6+`, `RQF 3-5`, `RQF 1-2`, `TSL` | a band button is pressed |
| `filter` | `occupation` | occupation name, or `ALL` | the occupation select changes |
| `select` | `country` | country name | a country is clicked, chosen in "Find a country", or opened with Enter |
| `open` | `country_detail` | country name | the country's occupation breakdown opens |
| `filter` | `country_detail_band` | `ALL`, `RQF 6+`, `RQF 3-5`, `RQF 1-2`, `TSL` | the band is changed inside that breakdown |

The figure sends no `download` event: the CSV button was removed from the note,
and with it the only download the figure offered.

`select` / `country` and `open` / `country_detail` always fire together, because
selecting a country is what opens its breakdown. Both are kept: the first counts
countries looked at, the second survives if the two are ever separated again.

## Deliberately not instrumented

Hover, pointer movement, focus, tooltip opening, scrolling the occupation list,
closing the breakdown, resize, fullscreen, deselection, and zoom or pan of any
kind (buttons, drag, pinch, wheel). These are not
committed actions; sending them would bury the signal and inflate event volume.
`action_value` is bounded: at most 144 occupation names and 26 country names,
both drawn from the payload, so cardinality cannot grow with traffic.
