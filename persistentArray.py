import json
import os

class PersistentArray:
    def __init__(self, num):
        self.file_path = "ownersArray/ownersArray.json"
        self.num = num
        self.array = self.load_array()  # Ensure that self.array is initialized

    # Load the array from the JSON file (or create a new one if it doesn't exist)
    def load_array(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                file_content = file.read()
                if file_content:  # Check if the file is not empty
                    return json.loads(file_content)  # Load the array from the file
                else:
                    return [None] * self.num  # Return default array if the file is empty
        else:
            return [None] * self.num  # Return default array if the file doesn't exist

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
        if index < len(self.array):
            self.array[index] = value
        else:
            self.array.append(value)  # If the index is out of bounds, append the value
        self.save_array()

    # Get the current array
    def get_array(self):
        return self.array
