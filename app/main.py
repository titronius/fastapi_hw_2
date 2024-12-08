from typing import List

from sqlalchemy import select
import crud
import models
import schema
import auth
from dependency import SessionDependency, TokenDependency

from fastapi import Depends, FastAPI, HTTPException
from lifespan import lifespan

app = FastAPI(title="Advertisement", version="0.1", description="Список объявлений*", lifespan=lifespan)

@app.post("/v1/advertisement/", response_model=schema.CreateAdvertisementResponse)
async def create_advertisement(
    session: SessionDependency,
    create_advertise_request: schema.CreateAdvertisementRequest,
    token: TokenDependency
    ):
    
    user_id = token.user.id
    create_advertisement_dict = create_advertise_request.model_dump()
    create_advertisement_dict["user_id"] = user_id
    advertisement = models.Advertisement(**create_advertisement_dict)
    await auth.check_access_rights(session, token, advertisement, write=True, read=False)
    await crud.add_item(session, advertisement)
    return advertisement.id_dict

@app.get("/v1/advertisement/{advertisement_id}", response_model=schema.GetAdvertisementResponse)
async def get_advertisement_by_id(
    session: SessionDependency,
    advertisement_id: int
    ):
    
    advertisement = await crud.get_item(session, models.Advertisement, advertisement_id)
    return advertisement.dict

@app.get("/v1/advertisement", response_model=List[schema.GetAdvertisementResponse])
async def get_advertisement_by_query(
    session: SessionDependency,
    get_advertisement_request: schema.GetAdvertisementsRequest = Depends()
    ):
    params_dict = get_advertisement_request.model_dump(exclude_none=True)
    advertisements = await crud.get_items(session, models.Advertisement, params_dict)
    return [advertise.dict for advertise in advertisements]

@app.patch("/v1/advertisement/{advertisement_id}", response_model=schema.UpdateAdvertisementResponse)
async def update_advertisement(
    session: SessionDependency,
    update_advertisement_request: schema.UpdateAdvertisementRequest,
    advertisement_id: int,
    token: TokenDependency
    ):
    
    advertisement = await crud.get_item(session, models.Advertisement, advertisement_id)
    await auth.check_access_rights(session, token, advertisement, write=True, read=False)
    advertisement_dict = update_advertisement_request.model_dump(exclude_none=True)
    for key, value in advertisement_dict.items():
        setattr(advertisement, key, value)
    await crud.add_item(session, advertisement)
    return advertisement.id_dict

@app.delete("/v1/advertisement/{advertisement_id}", response_model=schema.DeleteAdvertisementResponse)
async def delete_advertisement(
    session: SessionDependency,
    advertisement_id: int,
    token: TokenDependency
    ):
    
    advertisement = await crud.get_item(session, models.Advertisement, advertisement_id)
    await auth.check_access_rights(session, token, advertisement, write=True, read=False)
    await crud.delete_item(session, models.Advertisement, advertisement_id)
    return {"status" : "success"}

@app.post("/v1/user/", response_model=schema.CreateUserResponse)
async def create_user(
    session: SessionDependency, create_user_request: schema.CreateUserRequests
):

    create_user_dict = create_user_request.dict()
    create_user_dict["password"] = auth.hash_password(create_user_dict["password"])
    user = models.User(**create_user_dict)
    role = await auth.get_default_role(session)
    user.roles = [role]
    await crud.add_item(session, user)
    return user.id_dict

@app.get("/v1/user/{user_id}", response_model=schema.GetUserResponse)
async def get_user_by_id(
    session: SessionDependency,
    user_id: int
    ):
    
    user = await crud.get_item(session, models.User, user_id)
    return user.dict

@app.patch("/v1/user/{user_id}", response_model=schema.UpdateUserResponse)
async def update_user(
    session: SessionDependency,
    update_user_request: schema.UpdateUserRequest,
    user_id: int,
    token: TokenDependency
    ):
    
    user = await crud.get_item(session, models.User, user_id)
    await auth.check_access_rights(session, token, user, write=True, read=False, owner_field="id")
    user_dict = update_user_request.model_dump(exclude_none=True)
    for key, value in user_dict.items():
        setattr(user, key, value)
    await crud.add_item(session, user)
    return user.id_dict

@app.delete("/v1/user/{user_id}", response_model=schema.DeleteUserResponse)
async def delete_user(
    session: SessionDependency,
    user_id: int,
    token: TokenDependency
    ):
    
    user = await crud.get_item(session, models.User, user_id)
    await auth.check_access_rights(session, token, user, write=True, read=False, owner_field="id")
    await crud.delete_item(session, models.User, user_id)
    return {"status" : "success"}

@app.post("/v1/login/", response_model=schema.LoginResponse)
async def login(login_request: schema.LoginRequest, session: SessionDependency):
    name = login_request.name
    password = login_request.password
    user_query = select(models.User).where(models.User.name == name)
    user_model = await session.scalar(user_query)
    if user_model is None:
        raise HTTPException(401, "User or password is wrong")
    if not auth.check_password(user_model.password, password):
        raise HTTPException(401, "User or password is wrong")
    token = models.Token(user_id=user_model.id)
    await crud.add_item(session, token)
    return token.dict