# Writing style: examples

## Before and after

| Problem | Before | After |
| --- | --- | --- |
| Passive voice | The item is dropped when the header is corrupted. | The parser drops the item when the header is corrupted. |
| Compound tense | We have added a check for empty values. | We added a check for empty values. |
| Semicolon | The file is large; the tool refuses it. | The file is large. The tool refuses it. |
| Phrasal verb | Spin up one worker per batch. | Start one worker for each batch. |
| Noun from a verb | This performs a validation of the header. | This validates the header. |
| Noun cluster | the file header length field | the length field of the file header |
| Hedge stack | This may potentially help to improve speed. | This can make the run faster. |
| Marketing word | A blazing-fast parser. | The parser reads 2000 items in 15 s. |
| Idiom | This is a moving target. | This changes often. |
| Many names | the file ... the input ... the source | the file ... the file ... the file |
| Filler | Simply run the tests in order to check. | Run the tests to check. |

## Issue reply (strict mode)

Before:

> Thanks so much for reporting! It looks like this might be related to something weird in your setup,
> so we'd need you to grab some more info for us so we can dig into it.

After:

> Thank you for the report. To find the cause, we need more information:
>
> - The version of the package and of Python.
> - The full command that you used.
> - The full error output.
>
> Add this information as a comment to this issue.

## Commit subject

- Before: `fix: fixed a bug where timestamps were sometimes being read wrong`
- After: `fix: read timestamp 0 as 00:00:00 instead of a missing value`

## Code comment

Before:

```python
# we basically need to make sure we don't blow up on garbage data here
```

After:

```python
# Corrupted input is normal. Drop the item and continue.
```
