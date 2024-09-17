import json
import os

class PersistentArray:
    def __init__(self, num):
        if not self.array:  # If the loaded array is empty or invalid
            self.array = [None] * self.num  # Initialize a default array
            self.save_array()  # Save it to the file
        self.file_path = "ownersArray/ownersArray.json"
        self.array = self.load_array()
        self.num = num

    def load_array(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                file_content = file.read()
                if file_content:  # Check if the file is not empty
                    return json.loads(file_content)
                else:
                    return [None] * self.num  # If file is empty, return default array
        else:
            return [None] * self.num  # Return default array if file doesn't exist

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