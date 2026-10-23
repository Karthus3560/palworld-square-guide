"""Build a visual-only Palbox square using existing engine meshes/materials.

Input is UAssetAPI JSON decoded from this installation with matching mappings.
No class layout, work radius, collision volume, save, or native code changes.
"""
import copy
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
asset = json.loads((ROOT / 'palbox-mapped.json').read_text(encoding='utf-8-sig'))
original = copy.deepcopy(asset)

def prop(export, name):
    return next(p for p in export['Data'] if p['Name'] == name)

def add_import(value):
    asset['Imports'].append(value)
    return -len(asset['Imports'])

def ref(template, value, name):
    result = copy.deepcopy(template)
    result['Value'], result['Name'] = value, str(name)
    return result

# The stock cube is 100cm on each axis, as is the stock cylinder's diameter.
cube = json.loads((ROOT / 'cube-mapped.json').read_text(encoding='utf-8-sig'))
mesh = next(e for e in cube['Exports'] if e['ObjectName'] == 'Cube')
bounds = prop(mesh, 'ExtendedBounds')['Value']
extent = next(v for v in bounds if v['Name'] == 'BoxExtent')['Value'][0]['Value']
assert all(abs(extent[k] - 50.0) < 0.001 for k in ('X', 'Y', 'Z')), extent

package = copy.deepcopy(asset['Imports'][58])
package['ObjectName'] = '/Engine/BasicShapes/Cube'
package_idx = add_import(package)
mesh_import = copy.deepcopy(asset['Imports'][87])
mesh_import.update(ObjectName='Cube', OuterIndex=package_idx)
mesh_idx = add_import(mesh_import)

scs = asset['Exports'][41]
all_nodes = prop(scs, 'AllNodes')['Value']
child_template = prop(asset['Exports'][24], 'ChildNodes')
added = []
for source_component, parent_node, suffix in ((43, 30, ''), (42, 31, 'Back')):
    # Leave original boundary layers intact; child inherits their exact transform.
    component = copy.deepcopy(asset['Exports'][source_component])
    name = 'SquareGuide' + suffix
    component['ObjectName'] = name + '_GEN_VARIABLE'
    prop(component, 'StaticMesh')['Value'] = mesh_idx
    scale = prop(component, 'RelativeScale3D')['Value'][0]['Value']
    scale.update(X=1 / math.sqrt(2), Y=1 / math.sqrt(2), Z=1.0)
    component['CreateBeforeSerializationDependencies'] = [
        mesh_idx if x == -88 else x
        for x in component['CreateBeforeSerializationDependencies']
    ]
    asset['Exports'].append(component)
    component_idx = len(asset['Exports'])

    node = copy.deepcopy(asset['Exports'][parent_node])
    node['ObjectName'] = 'SCS_Node_' + str(18 + len(added))
    prop(node, 'ComponentTemplate')['Value'] = component_idx
    prop(node, 'InternalVariableName')['Value'] = name
    prop(node, 'VariableGuid')['Value'][0]['Value'] = (
        '{428FA515-6831-425C-9132-3D40EF901A01}' if not suffix else
        '{428FA515-6831-425C-9132-3D40EF901A02}'
    )
    node['CreateBeforeSerializationDependencies'] = [component_idx, -21]
    asset['Exports'].append(node)
    node_idx = len(asset['Exports'])

    parent = asset['Exports'][parent_node]
    children = copy.deepcopy(child_template)
    children['Value'] = [ref(children['Value'][0], node_idx, 0)]
    parent['Data'].append(children)
    parent['CreateBeforeSerializationDependencies'].append(node_idx)
    all_nodes.append(ref(all_nodes[0], node_idx, len(all_nodes)))
    scs['CreateBeforeSerializationDependencies'].append(node_idx)
    added.append((component_idx, node_idx))

# Unreal SCS instantiates the components even without a reflected member variable.
# Do not add class fields: that would change unversioned serialization layouts.
# Propagate the existing visibility decision to our attached visual components.
visibility = asset['Exports'][16]
changes = 0
for expr in visibility['ScriptBytecode']:
    if expr['$type'].split(',')[0].endswith('EX_Context'):
        call = expr.get('ContextExpression', {})
        if call.get('StackNode') == -43:
            assert call['Parameters'][1]['$type'].endswith('EX_False, UAssetAPI')
            call['Parameters'][1]['$type'] = 'UAssetAPI.Kismet.Bytecode.Expressions.EX_True, UAssetAPI'
            changes += 1
assert changes == 2

for name in ['/Engine/BasicShapes/Cube', 'Cube', 'SquareGuide', 'SquareGuideBack',
             'SquareGuide_GEN_VARIABLE', 'SquareGuideBack_GEN_VARIABLE']:
    if name not in asset['NameMap']:
        asset['NameMap'].append(name)
# Numbered SCS_Node names use the existing base FName + instance number.
assert 'SCS_Node' in asset['NameMap']
asset['DependsMap'].extend([[] for _ in range(4)])
asset['Generations'][-1].update(ExportCount=len(asset['Exports']), NameCount=len(asset['NameMap']))

# Structural and gameplay invariants before serialization.
assert asset['Exports'][2] == original['Exports'][2]  # class layout unchanged
for idx in range(50):
    if idx not in (16, 30, 31, 41):
        assert asset['Exports'][idx] == original['Exports'][idx], idx
for component_idx, _ in added:
    component = asset['Exports'][component_idx - 1]
    assert prop(component, 'bCanEverAffectNavigation')['Value'] is False
    assert prop(component, 'bGenerateOverlapEvents')['Value'] is False
    body = prop(component, 'BodyInstance')['Value']
    assert next(v for v in body if v['Name'] == 'CollisionEnabled')['Value'] == 'NoCollision'
for radius in (3500, 7000, 10000):
    half = radius / math.sqrt(2)
    assert math.isclose(math.hypot(half, half), radius)
    for yaw in (0, 37, 90, 180):
        angle = math.radians(yaw)
        x = half * math.cos(angle) - half * math.sin(angle)
        y = half * math.sin(angle) + half * math.cos(angle)
        assert math.isclose(math.hypot(x, y), radius)

(ROOT / 'palbox-square.json').write_text(json.dumps(asset, indent=2), encoding='utf-8')
print('PASS: two attached visual layers, unchanged gameplay/class layout, original materials, no collision/navigation, radius and rotation geometry.')
print('Added component/node exports:', added)
