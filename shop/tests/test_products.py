import pytest
from rest_framework.test import APIClient
from shop.models import Product, ProductOption, Tag


@pytest.mark.django_db
def test_create_product_with_nested_options_and_tags():
    client = APIClient()
    payload = {
        "name": "Coffee",
        "option_set": [
            {"name": "Small", "price": 3000},
            {"name": "Large", "price": 5000},
        ],
        "tag_set": [
            {"name": "beverage"},
            {"name": "hot"},
        ],
    }

    response = client.post("/shop/products/", payload, format="json")
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Coffee"
    assert len(data["option_set"]) == 2
    assert len(data["tag_set"]) == 2

    product = Product.objects.get(pk=data["pk"])
    assert product.option_set.count() == 2
    assert product.tag_set.count() == 2


@pytest.mark.django_db
def test_patch_product_sync_options_and_tags():
    client = APIClient()

    # 초기 생성
    create_payload = {
        "name": "Tea",
        "option_set": [
            {"name": "Hot", "price": 2500},
            {"name": "Iced", "price": 2700},
        ],
        "tag_set": [{"name": "beverage"}],
    }
    create_resp = client.post("/shop/products/", create_payload, format="json")
    assert create_resp.status_code == 201
    created = create_resp.json()
    product_id = created["pk"]

    # 기존 옵션/태그 상태 확인
    assert ProductOption.objects.filter(product_id=product_id).count() == 2
    assert Tag.objects.count() == 1

    # PATCH 동기화: 1) 기존 옵션 하나 수정, 2) 하나 제거, 3) 하나 추가
    # 태그는 beverage -> [caffeine, hot] 로 전체 교체
    existing_options = created["option_set"]
    keep_and_update = existing_options[0]

    patch_payload = {
        "name": "Tea Updated",
        "option_set": [
            {"pk": keep_and_update["pk"], "name": "Hot Updated", "price": 2600},
            {"name": "Milk", "price": 3000},
        ],
        "tag_set": [
            {"name": "caffeine"},
            {"name": "hot"},
        ],
    }

    patch_resp = client.patch(f"/shop/products/{product_id}/", patch_payload, format="json")
    assert patch_resp.status_code == 200

    # 옵션 2개로 동기화(수정+신규), 태그 2개로 동기화
    assert ProductOption.objects.filter(product_id=product_id).count() == 2
    updated_names = set(ProductOption.objects.filter(product_id=product_id).values_list("name", flat=True))
    assert updated_names == {"Hot Updated", "Milk"}

    tag_names = set(Tag.objects.values_list("name", flat=True))
    assert tag_names.issuperset({"caffeine", "hot"})


@pytest.mark.django_db
def test_get_product_returns_nested():
    client = APIClient()
    create_payload = {
        "name": "Latte",
        "option_set": [
            {"name": "Single", "price": 4000},
            {"name": "Double", "price": 5000},
        ],
        "tag_set": [{"name": "espresso"}],
    }
    resp = client.post("/shop/products/", create_payload, format="json")
    assert resp.status_code == 201
    product_id = resp.json()["pk"]

    get_resp = client.get(f"/shop/products/{product_id}/")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["name"] == "Latte"
    assert isinstance(data["option_set"], list) and len(data["option_set"]) == 2
    assert isinstance(data["tag_set"], list) and len(data["tag_set"]) == 1


@pytest.mark.django_db
def test_delete_product_deletes_options_but_keeps_tags():
    client = APIClient()
    payload = {
        "name": "Mocha",
        "option_set": [
            {"name": "Regular", "price": 4500},
        ],
        "tag_set": [{"name": "chocolate"}],
    }
    resp = client.post("/shop/products/", payload, format="json")
    assert resp.status_code == 201
    product_id = resp.json()["pk"]

    del_resp = client.delete(f"/shop/products/{product_id}/")
    assert del_resp.status_code == 204

    assert Product.objects.filter(pk=product_id).count() == 0
    assert ProductOption.objects.count() == 0
    # 태그는 남아 있어야 함
    assert Tag.objects.filter(name="chocolate").exists()


