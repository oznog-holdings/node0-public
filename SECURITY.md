# Reporting something that should not have been published

Everything here is meant to have passed a publication checklist that removes
addresses, credentials, serials, paths, private names and the details of the
finance system. If you find something that got through, an address, a credential
shape, a name, a detail that narrows a physical target, do not open a public
issue.

Use one of these, both private and both read by the maintainers:

- [Private vulnerability reporting](https://github.com/oznog-holdings/node0-public/security/advisories/new)
  on this repository.
- The contact in [oznog.com's security.txt](https://oznog.com/.well-known/security.txt).

Say where it is, page or file and line, and what you believe it exposes. You
will get an acknowledgement, and the fix goes out on the next push. Because a
mirror keeps history, a fix that has to remove something from the past is a
history rewrite at the origin followed by a fresh mirror, and any credential
that was exposed is rotated at its issuer regardless of how quickly the text
was removed. The maintainers will say which of those happened.

The tools under `tools/` are small and run locally on documentation; a
vulnerability in them is reported the same way.
