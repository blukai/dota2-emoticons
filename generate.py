import os
import shutil
import json
import vpk
import vdf
from PIL import Image

# Path to the bin that decompiles vtex_c into png
# https://github.com/SteamDatabase/ValveResourceFormat
decompiler = './decompiler/Decompiler.exe'

destination = './resources'
temp = './temp'

# Path to vpk, which contains all the emoticons
# windows d:/steam/SteamApps/common/dota 2 beta/game/dota/pak01_dir.vpk
# wsl     /mnt/d/steam/SteamApps/common/dota 2 beta/game/dota/pak01_dir.vpk
pak = vpk.open('/mnt/d/steam/SteamApps/common/dota 2 beta/game/dota/pak01_dir.vpk')
emoticons = vdf.loads(pak['scripts/emoticons.txt'].read().decode('utf-16le'))['emoticons']

destination_gif = destination + '/images/emoticons'
destination_json = destination + '/json'

with open(destination_json + '/emoticons.json', 'w') as f:
    f.write(json.dumps(emoticons, indent=4))
print('> Emoticons data saved in %s' % destination_json)

if not os.path.isdir(temp):
    os.mkdir(temp)

existing = os.listdir(destination_gif)

# get_name returns emote's filename without extension
def get_name(png):
    return png.replace('.png', '')

print('> Extracting from vpk')
for key, val in emoticons.items():
    name = get_name(val['image_name'])
    if name + '.gif' in existing:
        print('  - skipping existing "%s"' % name)
        continue
    pak['panorama/images/emoticons/' + name + '_png.vtex_c']\
        .save('%s/%s' % (temp, name + '.vtex_c'))

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
    os.system('convert -loop 0 -delay %d -alpha set -dispose previous %s/*.png %s/%s.gif' % (delay, directory, destination_gif, name))
    print('  - generated %s.gif' % name)

print('> Cleaning up')
shutil.rmtree(temp)
print('> Done!')
