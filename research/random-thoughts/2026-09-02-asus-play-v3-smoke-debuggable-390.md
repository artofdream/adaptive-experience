# ASUS v3 DEBUGGABLE + installer=null (#390)

> **Tags**: #aea #companion #honesty #play #gap-loop
> **Captured**: 2026-09-02
> **Issue**: #390

## Finding

Re-check after Need→Pay: installer=null, flags include DEBUGGABLE, versionCode 3.

## Build note

`release { isDebuggable = false }` set explicitly. Default was already false; explicit flag documents the gate. Same applicationId for debug+release (Firebase) means FAD/debug sideload can overwrite Play.

## Gate

Do not claim Play honesty for #387–#389 until ASUS shows Play-signed non-debuggable + installer=com.android.vending.
