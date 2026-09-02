# cts-ai Docker Desktop / WSL repair — 2026-09-02

> **Tags**: #aea #second-brain #devops #docker #wsl #cts-ai

## Incident

Docker Desktop emitted repeated Windows-path translation failures followed by
`getpwuid(0) failed` and `execvpe(/bin/sh) failed`. The Docker engine then
reported that Docker Desktop was unable to start.

## Findings

- WSL 2.7.11 and kernel 6.18.3.33.2 were installed and operational.
- `docker-desktop-data` had incorrectly become the default WSL distribution.
  It is a storage-only distribution and has neither a normal root user entry
  nor `/bin/sh`; invoking it as a login distribution reproduced the reported
  errors exactly.
- The `docker-desktop` distribution had a healthy `/bin/sh` and root account.
- Docker Desktop 4.89.0 was also configured with `UseLibkrun: true`, selecting
  the experimental Docker VMM. Its launcher and `libsailor` were mismatched;
  the backend log reported the missing `sailor_vm_pause` symbol.
- Two desktop installations were visible: current per-user 4.89.0 and an older
  Program Files 4.85.0 installation. The repair used the current per-user
  installation.

## Repair and validation

1. Changed WSL's default distribution from `docker-desktop-data` to
   `docker-desktop`, then shut WSL down cleanly.
2. Verified an unqualified WSL launch reached `/bin/sh` without translation or
   `getpwuid` errors.
3. Backed up Docker settings to
   `settings-store.before-wsl-repair-20260902.json` in the user's Docker
   roaming-data directory.
4. Disabled `UseLibkrun` and default-distro integration, retaining the stable
   WSL2 engine and avoiding integration with Docker's internal distro.
5. Restarted the current per-user Docker Desktop installation.

Post-repair evidence: Docker Desktop status `running`; server 29.7.2; two
existing containers and 25 images remained visible. No Docker data reset or
distribution unregister was performed.

## Durable lesson

Do not select `docker-desktop-data` as a user's default WSL distribution and do
not enable default-distro integration when the only registered distributions
are Docker's internal ones. A `getpwuid(0)` plus missing `/bin/sh` sequence is
expected when a storage-only distribution is treated as an interactive Linux
distribution. For ARM64 Docker VMM startup failures, inspect backend logs for
launcher/library symbol skew and return to WSL2 before considering a data reset.

Related: [[2026-09-02-session-memory-log-devops-companion-budget-florist-operator]]
