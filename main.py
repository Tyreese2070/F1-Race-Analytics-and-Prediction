import fastf1
import os

if os.path.isdir('cache') == False:
    os.mkdir('cache')
fastf1.Cache.enable_cache('cache')