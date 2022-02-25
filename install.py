import pathlib

# create configuration file
config_folder = pathlib.Path().home() / '.config' / 'lilasmr'
config_folder.mkdir(parents=True, exist_ok=True)

config_file = config_folder / 'config.ini'


with open(config_file, 'w') as c:
    c.write(f'''\
[Defaults]
PDFTitle = @filename
ScriptAuthor = lilellia

TeXPreamble = {pathlib.Path().home()}/.local/share/lilasmr/src/preamble.tex
''')
    
# create the executable
ex = pathlib.Path().home() / '.local' / 'bin' / 'lilasmr'
with open(ex, 'w') as f:
    f.write(f'''\
#!/bin/sh

python3 $HOME/.local/share/lilasmr/src/render.py "$@"''')

print('Install successful. To have an executable file, run:')
print('\tsudo chmod +x ~/.local/bin/lilasmr')