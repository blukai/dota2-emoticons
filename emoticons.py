import os
import vpk
import vdf
from PIL import Image

# Path to vpk, which contains all the emoticons
# windows d:/steam/SteamApps/common/dota 2 beta/game/dota/pak01_dir.vpk
# wsl     /mnt/d/steam/SteamApps/common/dota 2 beta/game/dota/pak01_dir.vpk
pak = vpk.open('/mnt/d/steam/SteamApps/common/dota 2 beta/game/dota/pak01_dir.vpk')
emoticons = vdf\
    .loads(pak['scripts/emoticons.txt'].read().decode('utf-16le'))['emoticons']\
    .items()

# Path to the tool that decompiles vtex_c into png
# https://github.com/SteamDatabase/ValveResourceFormat
decompiler = '/decompiler/Decompiler.exe -i %s -o %s'

destination = './assets/emoticons'
temp = './temp'

if not os.path.isdir(temp):
    os.mkdir(temp)

print('> Extracting from vpk')
for key, val in emoticons:
    name_vtex = val['image_name'].replace('.', '_') + '.vtex_c'
    name_png = val['image_name']
    # Temporarily save vtex_c emoticon
    pak['panorama/images/emoticons/' + name_vtex].save('%s/%s' % (temp, name_vtex))

print('> Decompiling')
os.system(os.getcwd() + decompiler % (temp, temp) + ' > /dev/null')

print('> Cutting the sequences and generating gifs')
total = len(emoticons)
for key, val in emoticons:
    name = val['image_name'].replace('.png', '')
    name_png = name + '_png.png'

    directory = ('%s/%s' % (temp, name))
    if not os.path.isdir(directory):
        os.mkdir(directory)

    img = Image.open('%s/%s' % (temp, name_png))
    # Frame count
    length = int(img.width / img.height)
    for i in range(length):
        img\
            .crop((i * img.height, 0, (i + 1) * img.height, img.height))\
            .save('%s/%02d.png' % (directory, i))

    delay = int(val['ms_per_frame']) / 10
    os.system('convert -loop 0 -delay %d -alpha set -dispose previous %s/*.png %s/%s.gif' % (delay, directory, destination, name))
    print('\t+ [%d/%d] %s.gif' % (i + 1, total, name))

print('cleaning up..')
os.rmdir(temp)
print('Done!')

