import json
class FilesRequest:
    def __init__(self, id:int) -> None:
        self.id = id
    def to_json(self):
        return json.dumps({'id': self.id})
    
    @classmethod
    def from_json(cls, data: str):
        try:
            # Load the JSON string into a dictionary
            json_data = json.loads(data)

            # Ensure the 'id' key is present in the data
            if 'id' not in json_data:
                raise ValueError("Missing 'id' field in JSON data")

            # Return a new instance of FilesRequest with the 'id'
            return cls(id=json_data['id'])

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error decoding JSON: {e}")
            raise