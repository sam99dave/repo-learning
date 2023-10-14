"""
-> First Steps
-> Path Parameters
-> Query Parameters
-> Request Body
-> Query Parameters & String Validations
-> Path Parameters & Numeric Validations
"""

from fastapi import FastAPI, Query, Path
from enum import Enum
from typing import Union, List
from typing_extensions import Annotated
from pydantic import BaseModel


app = FastAPI()

# First Step
@app.get("/")
async def root(inp):
    return {"message": f"Hello World {inp}"}

# Path Parameter
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

"""
Because path operations are evaluated in order, 
you need to make sure that the path for /users/me is declared before the one for /users/{user_id}
"""
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}

## Predefined Values
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}

## Path Parameters containing paths
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


# Query Parameters
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]

## Optional Parameters
@app.get("/item/{item_id}")
async def read_item(item_id: str, q: Union[str, None] = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

## Required Parameters
@app.get("/req-items/{item_id}")
async def read_user_item(item_id: str, needy: str):
    item = {"item_id": item_id, "needy": needy}
    return item

# Request Body
class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None

@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict
    # return item

## Request Body + Path Parameters
"""
FastAPI will recognize that the function parameters 
that match path parameters should be taken from the 
path, and that function parameters that are declared to be Pydantic models should be taken from the request body.

The function parameters will be recognized as follows:
-> If the parameter is also declared in the path, it will be used as a path parameter.
-> If the parameter is of a singular type (like int, float, str, bool, etc) it will be interpreted as a query parameter.
-> If the parameter is declared to be of the type of a Pydantic model, it will be interpreted as a request body.
"""
@app.put("/items/{item_id}")
async def create_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}

# Query Parameters & String Valdations

## -> Optional Query & Max length 50 validation
@app.get("/item-validation/")
async def read_items(q: Annotated[Union[str, None], Query(max_length=50)] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

## Add Regular Expression
@app.get("/item-regex/")
async def read_items(
    q: Annotated[
        Union[str, None], Query(min_length=3, max_length=50, pattern="^fixedquery$")
    ] = None
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

## Alternative way to declare required parameters
"""
Required with Ellipsis (...)
-> There's an alternative way to explicitly declare that a value is required. 
-> You can set the default to the literal value ...
"""
@app.get("/item-ellipsis/")
async def read_items(q: Annotated[str, Query(min_length=3)] = ...):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


## Query Parameter list/multiple values
"""
http://localhost:8000/item-list/?q=foo&q=bar
"""
@app.get("/item-list/")
async def read_items(q: Annotated[Union[List[str], None], Query()] = None):
    query_items = {"q": q}
    return query_items

## Add Query Metadata
@app.get("/query-metadata/")
async def read_items(
    q: Annotated[Union[str, None], 
                 Query(
                     title="Query string", 
                     description="Query string for the items to search in the database that have a good match",
                     min_length=3
                     )
                ] = None
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

## Alias Parameters
"""
Imagine that you want the parameter to be item-query
http://127.0.0.1:8000/items/?item-query=foobaritems

But item-query is not a valid Python variable name.
The closest would be item_query.
But you still need it to be exactly item-query...
Then you can declare an alias, and that alias is what will be used to find the parameter value:
"""
@app.get("/alias-param/")
async def read_items(q: Annotated[Union[str, None], Query(alias="item-query")] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

## Deprecating Parameters
"""
Now let's say you don't like this parameter anymore.
You have to leave it there a while because there are clients using it, but you want the docs to clearly show it as deprecated.
Then pass the parameter deprecated=True to Query:
"""

@app.get("/deprecate-param/")
async def read_items(
    q: Annotated[
        Union[str, None],
        Query(
            alias="item-query",
            title="Query string",
            description="Query string for the items to search in the database that have a good match",
            min_length=3,
            max_length=50,
            pattern="^fixedquery$",
            deprecated=True,
        ),
    ] = None
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

## Exclude From OpenAPI
"""
To exclude a query parameter from the generated OpenAPI schema (and thus, from the automatic documentation systems), 
set the parameter include_in_schema of Query to False:
"""

@app.get("/exclude-from-openapi/")
async def read_items(
    hidden_query: Annotated[Union[str, None], Query(include_in_schema=False)] = None
):
    if hidden_query:
        return {"hidden_query": hidden_query}
    else:
        return {"hidden_query": "Not found"}
    

# Path Parameters and Numeric Validations

@app.get("/path-validations/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="The ID of the item to get")],
    q: Annotated[Union[str, None], Query(alias="item-query")] = None,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

"""
Refer the doc for -> Order, defaults etc.
-> https://fastapi.tiangolo.com/tutorial/path-params-numeric-validations/
"""

## Number Validation: Greater than or Equal
@app.get("/path-ge/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=1)], q: str
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

@app.get("/path-gt-le/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="The ID of the item to get", gt=0, le=1000)],
    q: str,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

"""
Note::
When you import Query, Path and others from fastapi, they are actually functions.

That when called, return instances of classes of the same name.

So, you import Query, which is a function. And when you call it, it returns an instance of a class also named Query.

These functions are there (instead of just using the classes directly) so that your editor doesn't mark errors about their types.

That way you can use your normal editor and coding tools without having to add custom configurations to disregard those errors.
"""
