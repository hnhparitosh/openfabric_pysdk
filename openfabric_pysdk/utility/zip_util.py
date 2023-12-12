import json
import zlib
from typing import Any, Dict

from openfabric_pysdk.benchmark import MeasureBlockTime


#######################################################
#  Zip util
#######################################################
class ZipUtil:

    # ------------------------------------------------------------------------
    @staticmethod
    def decompress(data: bytes) -> Dict[str, Any]:
        with MeasureBlockTime("ZipUtil::decompress"):
            uncompressed = zlib.decompress(data)
            string: str = uncompressed.decode('utf-8')
            return json.loads(string)

    # ------------------------------------------------------------------------
    @staticmethod
    def compress(data: Dict[str, Any]) -> bytes:
        with MeasureBlockTime("ZipUtil::compress"):
            string = json.dumps(data)
            return zlib.compress(string.encode('utf-8'))
