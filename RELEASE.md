---
release type: patch
social_messages:
  x: >-
    {project_name} {version} is out! MaskErrors now also masks errors raised by
    other extensions' hooks. 🍓 https://strawberry.rocks/release/{version}
  linkedin: >-
    {project_name} {version} is out. The MaskErrors extension now masks errors
    raised inside other extensions' `on_parse`, `on_validate` and `on_execute`
    hooks, so their messages no longer reach clients from `execute` and
    `execute_sync`.
---

This release fixes `MaskErrors` not masking errors raised inside extension hooks
such as `on_parse`, `on_validate` and `on_execute` when using `Schema.execute`
or `Schema.execute_sync`. `Schema.stream` already masked them.

These errors are now handled before the `on_operation` hooks finish, so
`MaskErrors` and other operation extensions can process the error result. The
original error is still passed to `Schema.process_errors` for logging.
