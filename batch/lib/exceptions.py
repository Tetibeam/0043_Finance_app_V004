class DataLoadError(Exception):
    pass

class RawDataError(Exception):
    pass

class MissingFileError(DataLoadError):
    pass

class FileFormatError(DataLoadError):
    pass


