import os
import pathlib as ptl
import re
import json
TRIES = 5
"""Custom Model Data debug tool
"""

def dictprint(x: dict):
    for k, v in x.items():
        print(f'{k} = {v}')

curr = ptl.Path(__file__)

for x in range(TRIES): # Find .minecraft directory
    minecraft = curr.parents[x]
    
    if minecraft.stem == '.minecraft':
        break
    elif x == (TRIES - 1):
        raise FileNotFoundError('.minecraft directory not found.')

for x in range(TRIES): # Find No More Textures directory
    xmt = curr.parents[x]
    
    if xmt.stem == 'No More Textures':
        break
    elif x == (TRIES - 1):
        raise FileNotFoundError('No More Textures directory not found')

xmg = ptl.Path(minecraft / 'saves' / 'No More Games' / 'datapacks' / 'No More Games') # Find No More Games directory (hardcoded)
if not xmg.is_dir():
    raise FileNotFoundError('No More Games directory not found.', xmg)
data_src = [x for x in xmg.glob('**/*') if x.is_file()]

xmg_customs = []
for file in data_src:
    with open(file, 'r', encoding='UTF-8') as src:
        data = src.read()
        
        xmg_customs.extend(re.findall(r'(CustomModelData:[0-9]{6})', data))
xmg_customs = {int(s.removeprefix('CustomModelData:')) for s in xmg_customs} # Set of CustomModelData values used in the datapack


xmt = ptl.Path(xmt / 'assets' / 'minecraft' / 'models' / 'item')
if not xmt.is_dir():
    raise FileNotFoundError('No More Textures item models directory not found.', xmg)
data_src = [x for x in xmt.glob('**/*.json') if x.is_file()]

xmt_customs = {}
for file in data_src:
    with open(file, 'r', encoding='UTF-8') as src:
        data = json.load(src)
        
        if data.get('overrides'):
            for override in data.get('overrides'):
                cmdat = override.get('predicate').get('custom_model_data')
                xmt_customs[cmdat] = []
                model = override.get('model')
                if model:
                    modelpath = ptl.Path(xmt.parents[0] / model).with_suffix('.json')
                    if not modelpath.is_file():
                        raise FileNotFoundError(f'Item model {modelpath} not found.', xmg)
                    else:
                        with open(modelpath) as model_src:
                            model_data = json.load(model_src)
                            model_textures = model_data['textures'].values()
                            for mc_path in model_textures:
                                mc_path = mc_path.removeprefix('xmg:')
                                mc_path = ptl.Path(xmt.parents[2] / 'xmg' / 'textures' / mc_path).with_suffix('.png')
                                if not mc_path.is_file():
                                    raise FileNotFoundError(f'Texture {mc_path} not found.')
                                else:
                                    xmt_customs[cmdat].append(mc_path.relative_to(xmt.parents[3]))

with open(xmt.parents[3] / 'custompy.md', 'w') as custom: # Write results in file
    custom.write('## Implemented Codes\n')
    for n, k in enumerate([x for x in xmt_customs.keys() if x in xmg_customs], start=1):
        custom.write(f'{n}. {k}: ')
        for x in xmt_customs[k]:
            custom.write(f'<img src="{x.__str__()}" width="16"/>\n')
        custom.write('\n')
    custom.write('\n')
    
    custom.write('## World/Unimplemented Codes\n')
    for n, k in enumerate([x for x in xmt_customs.keys() if x not in xmg_customs], start=1):
        custom.write(f'{n}. {k}: ')
        for x in xmt_customs[k]:
            custom.write(f'<img src="{x.__str__()}" width="16"/>\n')
        custom.write('\n')