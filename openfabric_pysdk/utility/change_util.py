from hashlib import md5

from openfabric_pysdk.store import LRU


#######################################################
#  Change detector
#######################################################
class ChangeUtil:
    changes = LRU(500)

    @classmethod
    def is_changed(cls, name, content, serializer=None):
        if content is not None:
            content = serializer(content) if serializer is not None else content
        else:
            content = ''
        content_hash = cls.changes.get(name)
        new_content_hash = md5(str(content).encode('utf-8')).hexdigest()
        cls.changes.put(name, new_content_hash)
        return content_hash != new_content_hash
