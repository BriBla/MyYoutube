import os
import sys
import shutil
from pathlib import Path

class PathsUtils:
    #_public_path = os.path.join(sys.argv[0][0:-len(sys.argv[0].split('/')[-1])], "public")
    p_p = "/Users/briceblanchard/Documents/api3/"
    _public_path = os.path.join(p_p, "myYoutube", "public")
    _sources_path = os.path.join(_public_path, "sources")
    _formats_path = os.path.join(_public_path, "formats")

    @staticmethod
    def checkArbo():
        return (PathsUtils.checkExists(PathsUtils._public_path, True, True) and
                PathsUtils.checkExists(PathsUtils._sources_path, True, True) and
                PathsUtils.checkExists(PathsUtils._formats_path, True, True))
    
    @staticmethod
    def checkExists(path, directory=False, create=False):
        if os.path.exists(path):
            if directory and os.path.isfile(path):
                raise OSError("PathsUtils.checkExists: Requested directory is a file")
            return True
        if directory and create:
            os.mkdir(path)
            return True
        return False

    @staticmethod
    def getPublicPath():
        return PathsUtils._public_path

    @staticmethod
    def getSourcesPath():
        return PathsUtils._sources_path
    
    @staticmethod
    def getFormatsPath():
        return PathsUtils._formats_path


#PathsUtils.checkArbo()