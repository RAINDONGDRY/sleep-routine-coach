# Security policy

## Supported version

Security fixes are applied to the latest version on the default branch.

## Reporting

Report a suspected vulnerability through [GitHub private vulnerability reporting](https://github.com/RAINDONGDRY/sleep-routine-coach/security/advisories/new). Do not post user sleep data, credentials, channel identifiers, or exploit details in a public issue.

## Threat model

Relevant risks include:

- unintended local persistence without consent;
- overly broad file permissions;
- command injection through scheduler fields;
- reminders sent outside authorized hours or channels;
- user data entering Git, logs, exports, model prompts, or third-party messaging systems;
- a generated command being mistaken for authorization to execute it.

The implementation uses argument validation, standard-library JSON, atomic local writes, shell quoting for preview commands, no direct scheduler execution, and explicit consent gates. This does not replace host sandboxing, channel access control, encrypted disks, backups policy, or provider privacy controls.
