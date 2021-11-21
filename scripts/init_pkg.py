import os
import json

package = json.loads('{"schema_version": 1,"name": "MathEx","description": "Extension to the RPL++ math library","dependencies": [],"entry": "MathEx.rpl","js_module": "","author": "NishiOwO","version": "1.4.0C"}')

print('rpkg: action create_package started')
print('rpkg: create_package: creating initial directory structure')
if os.path.exists(package['name']) and os.path.isdir(package['name']):
    print('rpkg: create_package: create_directory: check_if_directory_exists: directory already exists')
else:
    print('rpkg: create_package: create_directory: creating directory')
    os.mkdir(package['name'])
print('rpkg: create_package: create_module_json: creating module json')
with open(package['name'] + '/module.json', 'w') as f:
    f.write(json.dumps(package))
print('rpkg: create_package: create_module_json: done')
print('rpkg: create_package: done')
print('rpkg: all actions complete')
print('rpkg: done')