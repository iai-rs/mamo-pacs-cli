import torch
import argparse
import os
import sys

sys.path.append("../")
from conv_model import CustomCNN, Model1

# Assuming you have a model class defined, import it
# from my_model import MyModelClass


def load_and_convert_model(file_path: str):
    # Check if the file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File {file_path} not found.")

    # Determine the output path with "_cpu.pth" suffix
    file_name, file_extension = os.path.splitext(file_path)
    output_file_path = f"{file_name}_cpu{file_extension}"

    # Load the model to CPU
    model = torch.load(file_path, map_location=torch.device("cpu"))

    # If you are loading a state dict, you need to initialize the model class and load the state dict
    # Uncomment and modify the following lines if you are loading a state dict instead of the full model
    # model = MyModelClass()  # Instantiate your model class
    # model.load_state_dict(torch.load(file_path, map_location=torch.device('cpu')))

    # Set the model to evaluation mode (optional, depending on your use case)
    model.eval()

    # Save the converted model
    torch.save(model, output_file_path)

    print(f"Model saved to {output_file_path}")


if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Convert PyTorch model to CPU")
    parser.add_argument("file_path", type=str, help="Path to the .pth model file")

    args = parser.parse_args()

    # Call the function to load and convert the model
    load_and_convert_model(args.file_path)
