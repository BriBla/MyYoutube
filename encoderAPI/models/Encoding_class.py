import ffmpeg
from threading import Lock


class Encoding:
    VALID_FORMATS = [144, 240, 360, 480, 720, 1080]
    ENCODINGS = []
    def __init__(self, source: str, id: int, mail: str):
        self._source = source
        self._id = id
        self._dimensions = self.setDims()
        self._width: int = self._dimensions[0]
        self._height: int = self._dimensions[1]
        self._possible_formats = [format for format in self.VALID_FORMATS if format <= self._height]
        self._targets = []
        self._max = max(self._possible_formats)
        self.mail = mail
        Encoding.ENCODINGS.append(self)
    
    @staticmethod
    def existsOrCreate(source: str, id: int, mail: str):
        for encoding in Encoding.ENCODINGS:
            encoding: Encoding
            if encoding._id == id:
                return encoding
        return Encoding(source, id, mail)

    @staticmethod
    def checkExists(id: int):
        for encoding in Encoding.ENCODINGS:
            encoding: Encoding
            if encoding._id == id:
                return encoding
        return None

    def setDims(self) -> tuple:
        probe = ffmpeg.probe(self._source)
        video_stream: dict = None
        for stream in probe["streams"]:
            if stream["codec_type"] == "video":
                video_stream = stream
                break
        return (int(video_stream["width"]), int(video_stream["height"]))

    def source(self) -> str:
        return self._source
    
    def width(self) -> int:
        return self._width
    
    def height(self) -> int:
        return self._height
    
    def dimensions(self) -> tuple:
        return (self._width, self._height)

    def possibleFormats(self) -> list:
        return self._possible_formats

    def targets(self) -> list:
        return self._targets
    
    def getTarget(self, target) -> bool:
        return target in self._targets
    
    def max(self) -> int:
        return self._max

    def addTarget(self, target) -> bool:
        if target not in self._possible_formats:
            raise ValueError("Given target resolution should not be higher than source resolution")
        mutex = Lock()
        mutex.acquire()
        success = False
        try:
            if not target in self._targets:
                self._targets.append(target)
                success = True
        finally:
            mutex.release()
        return success

    def popTarget(self, target) -> bool:
        try:
            self._targets.pop(self._targets.index(target))
            return True
        except (ValueError, KeyError):
            return False