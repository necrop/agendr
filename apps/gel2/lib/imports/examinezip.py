from zipfile import ZipFile

from .configreader import ConfigReader

def examine_zip(filepath):
    zipper = ZipFile(filepath)
    files = zipper.infolist()

    config_files = [f for f in files if f.filename.lower().endswith(".ini")]
    if config_files:
        config_file = zipper.open(config_files[0])
        config = ConfigReader(file=config_file)
    else:
        config = None

    xml_files = [zipper.open(f) for f in files
                 if f.filename.lower().endswith(".xml")]

    return (config, xml_files)
