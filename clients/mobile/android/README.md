# Android companion (M19)

Local Firebase config is **not** in git. Copy the real file from the Firebase
console next to this README's example:

`app/google-services.json.example` → `app/google-services.json`

Never commit `google-services.json`. `git check-ignore -v app/google-services.json`
must report the repo-root `.gitignore` rule.

## CI delivery

GitLab CI must inject the live file as a **protected file variable**
(`GOOGLE_SERVICES_JSON` or equivalent). Write it into `app/google-services.json`
in the job workspace only. Do not attach it as a pipeline artifact. Do not
paste the JSON into issues, MR notes, or research files.

Crashlytics and App Distribution wiring stay on #308. Key restriction or
rotation is recorded on #321 as date + package only — no key values.
