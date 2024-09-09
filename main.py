import fastapi
from fastapi import FastAPI, status, Query, Path, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from schemas import NewTour, SavedTour, TourPrice, DeletedTour
from storage import storage

app = FastAPI(
    debug=True,
    title='KolyanProject',
)

templates = Jinja2Templates(directory='templates')
app.mount('/static', StaticFiles(directory='static'), name='static')


def _serialize_tours(tours: list[tuple]) -> list[SavedTour]:
    for tour in tours:
        print(tour)
    tours_serialized = [
        SavedTour(
            id=tour[0],
            title=tour[1],
            description=tour[2],
            cover=tour[3],
            created_at=tour[4],
        )
        for tour in tours
    ]
    return tours_serialized


@app.get('/', include_in_schema=False)
@app.post('/', include_in_schema=False)
def index(request: Request, q: str = Form(default='')):
    tours = storage.get_tours(limit=40, q=q)
    context = {
        'request': request,
        'page_title': 'All tours',
        'products': tours
    }
    return templates.TemplateResponse('index.html', context=context)


@app.get('/{product_id}', include_in_schema=False)
def product_detail(request: Request, product_id: int):
    tour = storage.get_tours(product_id)
    context = {
        'request': request,
        'page_title': f'Product {tour.title}',
        'product': tour
    }
    return templates.TemplateResponse('details.html', context=context)


@app.get('/navigation/', include_in_schema=False)
def navigation(request: Request):
    context = {
        'request': request,
        'page_title': f'How to get to us',
    }
    return templates.TemplateResponse('navigation.html', context=context)


# CRUD


@app.post('/api/product/', description='create product', status_code=status.HTTP_201_CREATED, tags=['API', 'Product'])
def add_product(new_tour: NewTour) -> SavedTour:
    saved_product = storage.create_tour(new_tour)
    return saved_product


@app.get('/api/product/', tags=['API', 'Product'])
def get_products(
        limit: int = Query(default=5, description='no more than products', gt=0), q: str = '',
) -> list[SavedTour]:
    result = storage.get_tour(limit=limit, q=q)
    return result


@app.get('/api/product/{product_id}', tags=['API', 'Product'])
def get_product(product_id: int = Path(ge=1, description='product id')) -> SavedTour:
    result = storage.get_tour(product_id)
    return result


# UPDATE
@app.patch('/api/product/{product_id}', tags=['API', 'Product'])
def update_product_price(new_price: TourPrice,
                         product_id: int = Path(ge=1, description='product id')) -> SavedTour:
    result = storage.update_tour_price(product_id, new_price=new_price.price)
    return result


@app.delete('/api/product/{product_id}', tags=['API', 'Product'])
def update_tour_price(product_id: int = Path(ge=1, description='product id')) -> DeletedTour:
    storage.delete_tour(product_id)
    return DeletedTour(id=product_id)


@app.get('/all-tours', tags=['API', 'Product'])
@app.post('/search', tags=['API', 'Product'])
def all_tours(request: Request, search_text: str = Form(None)):
    if search_text:
        tours = storage.get_tour_by_title_or_other_str(query_str=search_text)
    else:
        tours = storage.get_tours(limit=15)
    tours_serialized = _serialize_tours(tours)
    context = {
        'title': f'Search result for text {search_text}' if search_text else 'our tours',
        'request': request,
        'tours': tours_serialized,

    }

    return templates.TemplateResponse('navbar.html', context=context)
