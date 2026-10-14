from pydantic import BaseModel
from typing import Optional

class Document(BaseModel):
      id: str
      filename: str
      file_type: str
      file_size: int
      page_count: Optional[int] = None
      extracted_text: str
 