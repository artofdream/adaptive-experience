# Android companion (M19)

Local Firebase config is **not** in git. Copy the real file from the Firebase
console next to this README's example:

`app/google-services.json.example` → `app/google-services.json`

Never commit `google-services.json`. `git check-ignore -v app/google-services.json`
must report the repo-root `.gitignore` rule.

## CI delivery

GitLab CI injects the live file as a **protected file variable** named
exactly `GOOGLE_SERVICES_JSON`. The job copies that file to
`app/google-services.json` in the job workspace only. Do not attach it as a
pipeline artifact. Do not paste the JSON into issues, MR notes, or research
files.

If `GOOGLE_SERVICES_JSON` is absent, `android-build-debug` copies
`app/google-services.json.example` so assemble still compiles. That dummy
cannot talk to the live Firebase project.

**Remaining sponsor step:** paste the live `google-services.json` into GitLab
CI/CD → Variables as a **protected, masked file** variable named
`GOOGLE_SERVICES_JSON`. Do not create that variable from an agent. Do not
commit the live file.

Crashlytics and App Distribution Gradle plugins are wired. No FCM / push
(ADR-019). Key restriction or rotation stays on #321 as date + package
only — no key values.
