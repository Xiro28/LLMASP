import json

def create_dataset_from_problems(filename: str, problems: set[str], samples: int) -> list[dict]:
    """
    Create a dataset filtered by the given problem names.

    Args:
        problems (set[str]): A set of problem names to filter the dataset.

    Returns:
        list[dict]: A list of dataset entries matching the specified problem names.
    """
    _dataset = get_dataset(filename, samples)
    return [obj for obj in _dataset if obj is not None and obj["problem_name"] in problems]


def get_dataset(filename: str, max_samples: int) -> list[dict]:
    """
    Load the entire dataset from the JSON file.

    Returns:
        list[dict]: The complete dataset.
    """
    dataset = json.load(open(filename, "r"))

    max_samples = max_samples - 1

    if max_samples > 0:
        samples = max_samples
        _new_dataset = []
        current_problem_name = "None"
        for obj in dataset:
            if samples > 0:
                current_problem_name = obj["problem_name"]
                _new_dataset.append(obj)
                samples -= 1
            elif samples <= 0:
                if current_problem_name == obj["problem_name"]:
                    _new_dataset.append(None)
                    continue

                samples = max_samples
                _new_dataset.append(obj)
        return _new_dataset

    return dataset