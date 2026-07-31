from pydantic import BaseModel
class M(BaseModel):
    a: int

try:
    M.model_validate_json('```json\n{"a": 1}\n```')
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
