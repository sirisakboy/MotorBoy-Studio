# python-can 4.6.1 — source/provenance note

- **Source:** PyPI `python-can==4.6.1`, official source distribution retained at `../source_archives/python_can-4.6.1.tar.gz`.
- **Archive SHA-256:** `290fea135d04b8504ebff33889cc6d301e2181a54099116609f940825ffe5005` (1,206,049 bytes).
- **License:** LGPL-3.0-only; `LICENSE.txt` is retained. Review obligations before linking/distributing.
- **Extracted subset:** `can/` runtime package plus `LICENSE.txt`, `README.rst`, `CHANGELOG.md`, `pyproject.toml`, and `setup.cfg`; tests, docs, examples, generated build outputs and unrelated source-package files are not expanded into this directory. Exact original sdist remains available for reproduction. `FILE_INDEX.csv` lists all 97 extracted files with size, SHA-256 and role.
- **Declared direct runtime dependencies:** `wrapt~=1.10`, `packaging>=23.1`, `typing_extensions>=3.10.0.0`; not vendored here. Some hardware backends need additional optional/vendor driver packages.
- **Intended role:** Python host-side CAN bus abstraction after a compatible interface/driver is installed. Contains many hardware-specific interface modules, but does not imply every adapter/OS is supported or available. Does not implement motorcycle OEM diagnostics or map profiles.
- **Verification:** imported the extracted source on Python 3.13.16 and passed a two-endpoint `virtual` bus send/receive smoke test. The sidecar in `adapters/can_jsonl_sidecar/` passed hardware-free virtual CAN tests. No physical CAN interface or vehicle was tested.
- **Safety:** the companion JSON-lines sidecar is local stdin/stdout only; CAN transmit is disabled by default and requires explicit `--allow-tx`. Even with transmit disabled, opening a physical backend may initialize its adapter. No CAN frame or ECU command is preconfigured.
