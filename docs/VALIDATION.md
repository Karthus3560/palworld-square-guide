# Validation — 1.0.0

Date: 23 October 2026. Steam build: 25246127. Screenshot game version: 1.0.5.102999.

- Original blueprint decode/encode: byte-identical `.uasset` and `.uexp`.
- Modified asset: 54 exports, all parsed successfully.
- Existing gameplay properties and generated-class layout: unchanged.
- Added guides: original blue materials, collision/overlaps/navigation disabled.
- Geometry: square corners match the parent circle at tested radii 35m, 70m and 100m, and rotations 0°, 37°, 90° and 180° (mathematical checks).
- Package extraction: byte-identical to staged files.
- Installed copy: hash matches built PAK.
- User gameplay confirmation: user reported “it works” and supplied the screenshot in `media/gameplay.png`.

The gameplay confirmation establishes visible operation on the tester's setup. It does not establish universal mod compatibility, performance gains, multiplayer compatibility, or tests of every base orientation/radius combination.

PAK SHA-256:

```text
8b341f5a5498603b8c7719e9a9fe97cb914819c3269d9bfde8d525c5c3c235f8
```

Version 1.0.0 packages the same PAK that was installed and confirmed working during the initial 0.1.0 test. No gameplay or visual changes were made between that test and this release.
