# Accepted input
example_input = {
	"patient_ids": ["id1", "id2", "id3", "id4", "id5"],
	"repeat_length": [20, 30, 40, 50, 75],
    "trans_id1": {
                "HGNC": "ILF3",
                "probeset_id1": {
                    "chromosome": "X",
                    "left_coord": 11023040,
                    "right_coord": 1459202,
                    "sequence": "ATATATCTGTGTCAC",
                    "intensities": [[1, 2, 1, 1], [1, 2, 1, 1], [1, 2, 1, 1], [1, 2, 1, 1], [1, 2, 1, 1]]
                },
                "probeset_id2": {
                    "chromosome": "X",
                    "left_coord": 11023040,
                    "right_coord": 1459202,
                    "sequence": "GTGCTCGATA",
                    "HGNC": "ILF3",
                    "intensities": [[1, 2, 1, 1], [1, 3, 4, 5], [1, 2, 1, 1], [1, 2, 1, 1], [1, 2, 1, 1]]
                },
                "probeset_id3": {
                    "chromosome": "X",
                    "left_coord": 11023040,
                    "right_coord": 1459202,
                    "sequence": "TATAGAGAGCACACCCTCTCG",
                    "HGNC": "ILF3",
                    "intensities": [[1, 2, 1, 1], [1, 2, 1, 1], [121, 120, 100, 1], [1, 2, 1, 1], [1, 2, 1, 1]]
                }
            }
}

# Produced output
example_output = {
	"patient_ids": ["id1", "id2", "id3", "id4", "id5"],
	"repeat_length": [20, 30, 40, 50, 75],
    "trans_id1": {
        "HGNC": "ILF3",
        "probeset_id1": 0.75,
        "probeset_id2": 0.000000000001,
        "probeset_id3": 0.9
    }
}


def compute_DASI(example_input):
    ...
    return example_output