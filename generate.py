import os
import shutil
import json
from collections import OrderedDict
import vpk
import vdf
from PIL import Image
import sys

# decompiler turns vtex_c into png
# https://github.com/SteamDatabase/ValveResourceFormat
decompiler = ''
# https://docs.python.org/3/library/sys.html#sys.platform
if sys.platform == 'darwin':
    decompiler = './Decompiler-osx-x64/Decompiler'
elif sys.platform == 'linux':
    decompiler = './Decompiler-linux-x64/Decompiler'
elif sys.platform == 'win32':
    decompiler = './Decompiler-windows-x64/Decompiler.exe'
else:
    sys.exit('unsupported platform')

if len(sys.argv) != 2:
    sys.exit('usage: python3 generate.py <path-to-dota>')

destination = './resources'
temp = './temp'

pak = vpk.open(sys.argv[1] + '/game/dota/pak01_dir.vpk')
emoticons = vdf.loads(pak['scripts/emoticons.txt'].read().decode('utf-16le'), mapper=OrderedDict)['emoticons']

destination_gif = destination + '/images/emoticons'
destination_json = destination + '/json'

with open(destination_json + '/emoticons.json', 'r+') as f:
    existing_emoticons = json.load(f)
    # merge existing and new emoticons
    emoticons = dict(list(existing_emoticons.items()) + list(emoticons.items()))
    f.seek(0)
    f.write(json.dumps(dict(list(existing_emoticons.items()) + list(emoticons.items())), indent=4))
print('> Emoticons data saved in %s' % destination_json)

if not os.path.isdir(temp):
    os.mkdir(temp)

existing = os.listdir(destination_gif)

# get_name returns emote's filename without extension
def get_name(png):
    return png.replace('.png', '')

print('> Extracting from vpk and generating char data')
charname = {}
for key, val in emoticons.items():
    name = get_name(val['image_name'])
    charname[chr(0xE000 + int(key))] = name
    if name + '.gif' in existing:
        print('  - skip existing "%s"' % name)
        continue
    try:
        pak['panorama/images/emoticons/' + name + '_png.vtex_c']\
            .save('%s/%s' % (temp, name + '.vtex_c'))
    except:
        print('  - could not extract "%s": %s' % (name, sys.exc_info()[0]))

with open(destination_json + '/charname.json', 'w') as f:
    f.write(json.dumps(charname, indent=4))
print('> Data `char:name` saved in %s' % destination_json)

print('> Decompiling')
os.system('%s -i %s -o %s > /dev/null' % (decompiler, temp, temp))

decompiled = []
for item in os.listdir(temp):
    if item.endswith('.png'):
        decompiled.append(item)

print('> Cutting the sequences and generating gifs')
for emote in decompiled:
    name = get_name(emote)
    directory = ('%s/%s' % (temp, name))
    if not os.path.isdir(directory):
        os.mkdir(directory)
    img = Image.open('%s/%s.png' % (temp, name))
    # Frame count
    length = int(img.width / img.height)
    for i in range(length):
        img\
            .crop((i * img.height, 0, (i + 1) * img.height, img.height))\
            .save('%s/%02d.png' % (directory, i))

    delay = int(val['ms_per_frame']) / 10
    # combines the sequence images into a gif using imagemagick
    os.system('convert -loop 0 -delay %d -alpha set -dispose previous %s/*.png %s/%s.gif' % (delay, directory, destination_gif, name))
    print('  - generated %s.gif' % name)

print('> Cleaning up')
shutil.rmtree(temp)
print('> Done!')
