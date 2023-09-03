"""
-> Body - Multiple Parameters

"""
from typing import Union

from fastapi import FastAPI, Path, Body
from pydantic import BaseModel
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