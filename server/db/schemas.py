from pydantic import BaseModel


class BaseResponse(BaseModel):
    result: bool

class BaseRecipe(BaseModel):
    title: str
    time_cooking: int


class AllRecipesOut(BaseRecipe):
    id_recipe: int
    count_views: int

    class Config:
        from_attributes = True


class RecipeIn(BaseRecipe):
    ingredients: str
    description: str


class RecipeOut(BaseRecipe):
    id_recipe: int
    ingredients: str
    description: str

    class Config:
        from_attributes = True


