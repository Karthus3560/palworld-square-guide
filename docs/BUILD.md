# Build notes

The release uses a PAK asset override, not executable injection. The source transformation is in `src/build_guide.py`. Original extracted game assets, mapping files, third-party tools and their binaries are intentionally absent from this repository.

## Reproduce from your own installation

1. Obtain UAssetGUI/UAssetAPI, repak and a Palworld `.usmap` matching your game build from their upstream projects linked in the README.
2. In a private build directory, extract these assets and their `.uexp` companions from your own `Pal-Windows.pak`:
   - `Pal/Content/Pal/Blueprint/MapObject/BuildObject/BP_BuildObject_PalBoxV2.uasset`
   - `Engine/Content/BasicShapes/Cube.uasset`
3. Convert the assets to UAssetAPI JSON using Unreal Engine 5.1 and the matching mappings. Name the results `palbox-mapped.json` and `cube-mapped.json`.
4. Before patching, convert the original Palbox JSON back to assets and verify both files are byte-identical to the originals. The release build passed this check.
5. Copy `src/build_guide.py` beside those JSON files and run it with Python 3. It writes `palbox-square.json`.
6. Convert that JSON back to `stage/Pal/Content/Pal/Blueprint/MapObject/BuildObject/BP_BuildObject_PalBoxV2.uasset`, using the same mappings.
7. Decode the resulting asset again. Check that all 54 exports parse and all original gameplay properties and class fields are unchanged.
8. Pack `stage` with repak, mount point `../../../`, PAK V11, as `PalboxSquareGuide_P.pak`. Re-extract the package and compare bytes with the staged assets.

UAssetGUI CLI syntax varies by version; follow the upstream instructions. The release was built using UAssetGUI 1.1.0 and repak 0.2.2. Tool runtimes and decompression libraries may be required on the build machine; they are not dependencies for players.

## Implementation

Two added SCS component templates use `/Engine/BasicShapes/Cube`. They are children of the existing `AreaRange` and `AreaRange1` construction nodes. The cube and cylinder both have 100cm XY bounds, so child XY scale `1/sqrt(2)` produces an inscribed square; Z scale remains 1.

The templates retain the respective original boundary material. Collision, overlaps and navigation influence are disabled. Two existing `SetHiddenInGame` calls propagate their visibility decision to children. No new ticking code or generated-class fields are introduced.

The transformation deliberately asserts the known build's structure. It should not be applied blindly after an update. Adapting to a different blueprint requires inspection and fresh gameplay testing.
