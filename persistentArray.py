import json
import os

class PersistentArray:
    def __init__(self, num):
        self.file_path = "ownersArray/ownersArray.json"
        self.array = self.load_array()
        self.num = num

    # Load the array from the JSON file (or create a new one if it doesn't exist)
    def load_array(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                return json.load(file)
        else:
            return [None] * self.num  # Default empty array if no file exists

    # Save the array to the JSON file
    def save_array(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.array, file)

    # Method to explicitly update the array
    def update_array(self, index, value):
        if 0 <= index < len(self.array):
            self.array[index] = value
        else:
            self.array.append(value)
        self.save_array()

    # Add an item to the array
    def add_to_array(self, value, index):
        if 0 <= index < len(self.array):
            self.array[index] = value  # Replace the value at the given index
        else:
            # If the index is out of bounds, you can choose to append the value instead
            self.array.append(value)
        self.save_array()

    # Get the current array
    def get_array(self):
        return self.array