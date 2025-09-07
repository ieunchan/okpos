from drf_writable_nested import WritableNestedModelSerializer
from .models import Product, ProductOption, Tag


class TagSerializer(WritableNestedModelSerializer):
    class Meta:
        model = Tag
        fields = ['pk', 'name']

    def create(self, validated_data):
        # name 기반으로 get_or_create, 중복 태그 방지
        tag, _ = Tag.objects.get_or_create(**validated_data)
        return tag


class ProductOptionSerializer(WritableNestedModelSerializer):
    class Meta:
        model = ProductOption
        fields = ['pk', 'name', 'price']


class ProductSerializer(WritableNestedModelSerializer):
    option_set = ProductOptionSerializer(many=True, required=False)
    tag_set = TagSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ['pk', 'name', 'option_set', 'tag_set']

    def create(self, validated_data):
        option_set_data = validated_data.pop('option_set', [])
        tag_set_data = validated_data.pop('tag_set', [])

        product = Product.objects.create(**validated_data)

        # Tags: name 기반으로 set (전체 동기화 의미로 set 사용)
        if tag_set_data is not None:
            tags = []
            for tag_data in tag_set_data:
                tag_name = tag_data.get('name')
                if not tag_name:
                    # 방어적 처리: name 누락 시 skip
                    continue
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                tags.append(tag)
            product.tag_set.set(tags)

        # Options: product에 연결하여 모두 생성
        for opt_data in option_set_data:
            # pk/id는 무시하고 필요한 필드만 사용
            ProductOption.objects.create(
                product=product,
                name=opt_data.get('name'),
                price=opt_data.get('price'),
            )

        return product

    def update(self, instance, validated_data):
        option_set_data = validated_data.pop('option_set', None)
        tag_set_data = validated_data.pop('tag_set', None)

        # 기본 필드 업데이트
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        # Tag 동기화: payload가 주어졌을 때만 전체 동기화
        if tag_set_data is not None:
            tags = []
            for tag_data in tag_set_data:
                tag_name = tag_data.get('name')
                if not tag_name:
                    continue
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                tags.append(tag)
            instance.tag_set.set(tags)

        # Option 동기화: payload가 주어졌을 때만 전체 동기화
        if option_set_data is not None:
            existing_options = {opt.pk: opt for opt in instance.option_set.all()}
            kept_ids = set()

            for opt_data in option_set_data:
                opt_id = opt_data.get('pk') or opt_data.get('id')
                if opt_id and opt_id in existing_options:
                    opt_obj = existing_options[opt_id]
                    if 'name' in opt_data:
                        opt_obj.name = opt_data['name']
                    if 'price' in opt_data:
                        opt_obj.price = opt_data['price']
                    opt_obj.save()
                    kept_ids.add(opt_obj.pk)
                else:
                    new_opt = ProductOption.objects.create(
                        product=instance,
                        name=opt_data.get('name'),
                        price=opt_data.get('price'),
                    )
                    kept_ids.add(new_opt.pk)

            # payload에 없는 기존 옵션 삭제
            for exist_id, exist_obj in existing_options.items():
                if exist_id not in kept_ids:
                    exist_obj.delete()

        return instance