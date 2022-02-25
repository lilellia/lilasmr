import pathlib
import shutil
import stat

# root of this repository
ROOT = pathlib.Path(__file__).parent


def is_executable(fp: pathlib.Path) -> bool:
    """ Return whether the user has execute permissions on the given file. """
    return bool(fp.stat().st_mode & stat.S_IXOTH)


def main():
    # create path to config file ($HOME/.local/lilasmr)
    config_folder = pathlib.Path().home() / '.config' / 'lilasmr'
    config_folder.mkdir(parents=True, exist_ok=True)

    # copy default configuration file to $CONFIG_FOLDER / config.ini
    default_config = ROOT / 'static' / 'default-config.ini'
    shutil.copy(default_config, config_folder / 'config.ini')
        
    # copy the executable to $HOME/.local/bin
    # after ensuring the directory exists
    bin = pathlib.Path().home() / '.local' / 'bin'
    bin.mkdir(parents=True, exist_ok=True)
    
    exec_dest = bin / 'lilasmr'
    shutil.copy(ROOT / 'static' / 'lilasmr', exec_dest)

    print('Install successful.')
    
    if not is_executable(exec_dest):
        print(f'{exec_dest} file is not executable. Run:')
        print('\tsudo chmod +x ~/.local/bin/lilasmr')
    

if __name__ == "__main__":
    main()