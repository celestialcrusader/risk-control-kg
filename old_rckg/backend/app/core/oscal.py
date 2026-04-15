from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class Property(BaseModel):
    name: str
    value: str
    ns: Optional[str] = None

class Link(BaseModel):
    href: str
    rel: Optional[str] = None
    text: Optional[str] = None

class Control(BaseModel):
    id: str
    class_: Optional[str] = Field(None, alias="class")
    title: str
    params: List[Dict] = []
    props: List[Property] = []
    links: List[Link] = []
    parts: List[Dict] = [] # Simplified for now
    controls: List['Control'] = [] # Nested controls

class Group(BaseModel):
    id: Optional[str] = None
    class_: Optional[str] = Field(None, alias="class")
    title: str
    params: List[Dict] = []
    props: List[Property] = []
    links: List[Link] = []
    parts: List[Dict] = []
    groups: List['Group'] = []
    controls: List[Control] = []

class Metadata(BaseModel):
    title: str
    last_modified: str = Field(..., alias="last-modified")
    version: str
    oscal_version: str = Field(..., alias="oscal-version")
    props: List[Property] = []
    links: List[Link] = []

class Catalog(BaseModel):
    uuid: str
    metadata: Metadata
    groups: List[Group] = []
    controls: List[Control] = []
