from pathlib import Path
import numpy as np

from olmo.mm_data.data_store import TextChunk, ImageChunk, ExampleReader, MMStorageConfig
from olmo.mm_data.image_token_size import PerPatch
from olmo.mm_data.structure_index import BasicIndexer, ExampleInfo


def _tokens(*data):
    return TextChunk(np.array(data, np.uint16), False)


def _mtokens(*data):
    return TextChunk(np.array(data, np.uint16), True)


def test_indexer(tmp_path: Path):
    rng = np.random.RandomState(59018)
    index_f = tmp_path.joinpath("index.bin")
    indexer = BasicIndexer()
    sz = PerPatch(1, 1)

    def _image(w, h):
        object_id = rng.randint(0, 256, (32,), dtype=np.uint8).tobytes()
        return ImageChunk(object_id, w, h, sz(w, h))

    data = [
        [_tokens(31, 52, 91), _mtokens(21)],
        [_image(1, 3), _tokens(5), _mtokens(19)],
        [_image(3, 2), _tokens(67), _image(2, 2), _tokens(98, 1, 17)],
        [_mtokens(2, )],
        [_tokens(13), _image(2, 1), _image(2, 2)],
    ]
    indexer.write_index(index_f, [(0, 0, x) for x in data])
    reader = ExampleReader(None, sz, None, MMStorageConfig())
    out = list(indexer.get_indices(index_f, 0, reader))
    offset = 0
    assert len(out) == len(data)
    for actual, ex in zip(out, data):
        expected_struct = ExampleInfo.from_example(offset, ex)
        assert expected_struct == actual
        offset += expected_struct.num_bytes + 2
