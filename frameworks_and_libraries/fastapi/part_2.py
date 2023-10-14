"""
-> Body - Multiple Parameters
-> Body - Fields
-> Body - Nested Models
"""
from typing import Union, Set, List, Dict

from fastapi import FastAPI, Path, Body
from pydantic import BaseModel, Field, HttpUrl
from typing_extensions import Annotated

app = FastAPI()


class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None


@app.put("/items/{item_id}")
async def update_item(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
    q: Union[str, None] = None,
    item: Union[Item, None] = None,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if item:
        results.update({"item": item})
    return results

## Multiple Body Parameters
class User(BaseModel):
    username: str
    full_name: Union[str, None] = None


@app.put("/multiple-body/{item_id}")
async def update_item(item_id: int, item: Item, user: User):
    results = {"item_id": item_id, "item": item, "user": user}
    return results

## Singular Values in Body
"""
- Passing Singular values as it is triggers FastAPI to consider it as query
- Annotated provides Body to solve this issue
"""
@app.put("/singular-in-body/{item_id}")
async def update_item(
    item_id: int, item: Item, user: User, importance: Annotated[int, Body()]
):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results

## Embed a single body parameter
"""
Learn about the usecase at -> https://fastapi.tiangolo.com/tutorial/body-multiple-params/#embed-a-single-body-parameter
"""
@app.put("/embed-in-body/{item_id}")
async def update_item(item_id: int, item: Annotated[Item, Body(embed=True)]):
    results = {"item_id": item_id, "item": item}
    return results

# Body - Fields
class ItemNew(BaseModel):
    name: str
    description: Union[str, None] = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: Union[float, None] = None

@app.put("/body-field/{item_id}")
async def update_item(item_id: int, item: Annotated[ItemNew, Body(embed=True)]):
    results = {"item_id": item_id, "item": item}
    return results

# Body - Nested Models

class Image(BaseModel):
    url: str
    name: str

class ItemNested(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    tags: Set[str] = set()
    image: Union[Image, None] = None

@app.put("/nested-models/{item_id}")
async def update_item(item_id: int, item: ItemNested):
    results = {"item_id": item_id, "item": item}
    return results

"""
Here in the above code snippet, the sub-model -> Image
is used as a type for attribute image in ItemNested
"""

## Special types and validation

class ImageSpecial(BaseModel):
    url: HttpUrl
    name: str

class ItemSpecial(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    tags: Set[str] = set()
    image: Union[ImageSpecial, None] = None

@app.put("/special-types/{item_id}")
async def update_item(item_id: int, item: ItemSpecial):
    results = {"item_id": item_id, "item": item}
    return results


## Deeply Nested Models

class ImageDeep(BaseModel):
    url: HttpUrl
    name: str

class ItemDeep(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    tags: Set[str] = set()
    images: Union[List[ImageDeep], None] = None

class Offer(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    items: List[ItemDeep]

@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer


## Bodies of arbitrary dicts
"""
In this case, you would accept any dict as long as it has int keys with float values:

NOTE
Have in mind that JSON only supports str as keys.
But Pydantic has automatic data conversion.
This means that, even though your API clients can only send strings as keys, as long as those strings contain pure integers, Pydantic will convert them and validate them.
And the dict you receive as weights will actually have int keys and float values.
"""
@app.post("/index-weights/")
async def create_index_weights(weights: Dict[int, float]):
    return weights