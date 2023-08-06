import torch

def inspect_state_dict(model_path):
    # Load state_dict from the specified file
    state_dict = torch.load(model_path, map_location='cpu')

    # Get the keys in the state_dict
    keys = state_dict.keys()

    print(f"Total number of keys in {model_path}: {len(keys)}")
    print("Keys:")
    for key in keys:
        print(key)

    return keys

if __name__ == "__main__":
    model_path = "./weights/SGHM-ResNet50.pth"
    inspect_state_dict(model_path)
